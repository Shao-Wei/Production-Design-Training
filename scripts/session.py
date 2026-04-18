#!/usr/bin/env python3
"""End-session workflow and forget-safe fallback helpers."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "STATE.json"
END_PATH = ROOT / "docs" / "status" / "END_OF_DAY.md"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_state() -> dict[str, Any]:
    if not STATE_PATH.exists():
        return {}
    return json.loads(STATE_PATH.read_text())


def save_state(state: dict[str, Any]) -> None:
    state["updated_at"] = now_iso()
    STATE_PATH.write_text(json.dumps(state, indent=2) + "\n")


def run_step(label: str, command: list[str]) -> tuple[str, int]:
    print(f"== {label}", flush=True)
    completed = subprocess.run(command, cwd=ROOT)
    print(f"{label}: exit {completed.returncode}", flush=True)
    return label, completed.returncode


def render_end_summary(state: dict[str, Any], steps: list[tuple[str, int]], args: argparse.Namespace) -> str:
    status = state.get("status", {})
    focus = state.get("focus", {})
    active = focus.get("active_study", {})
    chat = state.get("chat", {})
    next_actions = focus.get("next_actions", [])

    step_lines = [f"- {label}: {'PASS' if code == 0 else f'FAIL ({code})'}" for label, code in steps]
    next_lines = [f"- {action}" for action in next_actions[:3]] or ["- Pick the next concrete learning action."]

    checklist = [
        "- [ ] Review `docs/status/RESUME.md`.",
        "- [ ] Review `docs/status/ROLLING_SUMMARY.md`.",
        "- [ ] Review this end-of-day summary.",
        "- [ ] Manually commit finished stage/work, if ready.",
        "- [ ] Rename/update planning thread.",
        "- [ ] Rename/update implementation/Codex thread.",
        "- [ ] Start next session from `python3 scripts/workflow_alias.py resume`.",
    ]

    if args.weekly:
        checklist.insert(3, "- [ ] Review weekly retention entry.")
    if args.monthly:
        checklist.insert(3, "- [ ] Review monthly retention entry.")

    lines = [
        "# End Of Day Summary",
        "",
        f"Generated: {now_iso()}",
        "",
        "## Maintenance",
        *step_lines,
        "",
        "## Learning Continuity",
        f"- Current focus: {active.get('title', 'n/a')} ({focus.get('active_phase', 'n/a')})",
        f"- Progress: {status.get('overall_tasks_done', 0)}/{status.get('overall_tasks_total', 0)} tasks complete ({status.get('overall_percent', 0)}%).",
        *next_lines,
        "",
        "## Thread Handling",
        f"- Last known thread: {chat.get('last_thread') or 'not set'}",
        f"- Resume hint: {chat.get('resume_instruction') or 'not set'}",
        "- Keep planning thread and implementation/Codex thread separate.",
        "",
        "## Human Checklist",
        *checklist,
    ]
    return "\n".join(lines) + "\n"


def mark_end_session(state: dict[str, Any], summary_path: Path, steps: list[tuple[str, int]]) -> None:
    state.setdefault("end_session", {})
    state["end_session"].update(
        {
            "last_end_at": now_iso(),
            "last_summary": str(summary_path.relative_to(ROOT)),
            "last_steps": [
                {"label": label, "exit_code": code}
                for label, code in steps
            ],
            "fallback_needed": False,
        }
    )
    save_state(state)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run end-session maintenance and write a human checklist.")
    parser.add_argument("--weekly", action="store_true", help="Also run weekly retention compression.")
    parser.add_argument("--monthly", action="store_true", help="Also run monthly retention consolidation.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    steps: list[tuple[str, int]] = []

    steps.append(run_step("progress refresh", [sys.executable, str(ROOT / "scripts" / "update_progress.py")]))
    steps.append(run_step("recap update", [sys.executable, str(ROOT / "scripts" / "resume_now.py"), "--mode", "now"]))

    if args.weekly:
        steps.append(run_step("weekly retention", [sys.executable, str(ROOT / "scripts" / "resume_now.py"), "--mode", "weekly"]))
    if args.monthly:
        steps.append(run_step("monthly retention", [sys.executable, str(ROOT / "scripts" / "resume_now.py"), "--mode", "monthly"]))

    state = load_state()
    END_PATH.parent.mkdir(parents=True, exist_ok=True)
    summary = render_end_summary(state, steps, args)
    END_PATH.write_text(summary)
    mark_end_session(state, END_PATH, steps)

    print()
    print(f"End-of-day summary written to {END_PATH.relative_to(ROOT)}")
    print()
    print(summary.rstrip())

    return 0 if all(code == 0 for _, code in steps) else 1


if __name__ == "__main__":
    raise SystemExit(main())
