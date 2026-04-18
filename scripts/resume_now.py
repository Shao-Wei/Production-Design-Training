#!/usr/bin/env python3
"""Generate a concise resume recap and maintain compact project memory."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import update_progress


ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "STATE.json"
RESUME_PATH = ROOT / "docs" / "status" / "RESUME.md"
ROLLING_PATH = ROOT / "docs" / "status" / "ROLLING_SUMMARY.md"

MAX_LEARNING_HISTORY = 20
MAX_WORKFLOW_HISTORY = 20
MAX_CHAT_HISTORY = 20
MAX_RECENT_FILES = 6

DEFAULT_STATE: dict[str, Any] = {
    "schema_version": 1,
    "project": "Production Design",
    "updated_at": "",
    "resume": {
        "last_run_at": "",
        "last_mode": "",
        "confidence": 0.0,
    },
    "focus": {
        "active_phase": "",
        "active_study": {
            "kind": "",
            "id": "",
            "title": "",
            "folder": "",
        },
        "next_actions": [],
        "blockers": [],
    },
    "status": {
        "overall_tasks_done": 0,
        "overall_tasks_total": 0,
        "overall_percent": 0,
        "studies_complete": 0,
        "studies_total": 0,
        "phase_summary": [],
    },
    "retention": {
        "weekly": [],
        "monthly": [],
    },
    "context": {
        "learning_history": [],
        "workflow_history": [],
        "chat_history": [],
        "recent_files": [],
    },
    "chat": {
        "last_thread": "",
        "resume_instruction": "",
    },
}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_state() -> dict[str, Any]:
    if not STATE_PATH.exists():
        return json.loads(json.dumps(DEFAULT_STATE))

    try:
        loaded = json.loads(STATE_PATH.read_text())
        merged = json.loads(json.dumps(DEFAULT_STATE))
        merged.update(loaded)

        for key in ("resume", "focus", "status", "retention", "context", "chat"):
            if isinstance(loaded.get(key), dict):
                merged[key].update(loaded[key])

        return merged
    except json.JSONDecodeError:
        return json.loads(json.dumps(DEFAULT_STATE))


def save_state(state: dict[str, Any]) -> None:
    state["updated_at"] = now_iso()
    STATE_PATH.write_text(json.dumps(state, indent=2) + "\n")


def build_status(studies: list[update_progress.Study]) -> dict[str, Any]:
    completed = sum(study.done for study in studies)
    total = sum(study.total for study in studies)
    percent = round((completed / total) * 100) if total else 0
    complete_studies = sum(1 for study in studies if study.total and study.done == study.total)

    phases = sorted({study.phase for study in studies})
    phase_summary: list[dict[str, Any]] = []
    for phase in phases:
        phase_done = sum(study.done for study in studies if study.phase == phase)
        phase_total = sum(study.total for study in studies if study.phase == phase)
        phase_percent = round((phase_done / phase_total) * 100) if phase_total else 0
        phase_summary.append(
            {
                "phase": phase,
                "done": phase_done,
                "total": phase_total,
                "percent": phase_percent,
            }
        )

    return {
        "overall_tasks_done": completed,
        "overall_tasks_total": total,
        "overall_percent": percent,
        "studies_complete": complete_studies,
        "studies_total": len(studies),
        "phase_summary": phase_summary,
    }


def detect_focus(studies: list[update_progress.Study]) -> dict[str, Any]:
    active = next((study for study in studies if study.done < study.total), None)
    if active is None and studies:
        active = studies[-1]

    if active is None:
        return {
            "active_phase": "",
            "active_study": {
                "kind": "",
                "id": "",
                "title": "",
                "folder": "",
            },
            "next_actions": ["Pick the next scene and create a new study block."],
            "blockers": [],
        }

    study_id = active.bonus_index if active.kind == "bonus" else (active.number or "")
    folder_prefix = "Bonus Scene Study" if active.kind == "bonus" else "Scene Study"
    folder_name = f"{folder_prefix} #{study_id} {active.title}".replace("##", "#")

    next_actions = [
        f"{active.title}: finish {task}" for task in active.missing[:3]
    ]
    if not next_actions:
        next_actions = ["Pick the next scene and scaffold the next study."]

    return {
        "active_phase": active.phase,
        "active_study": {
            "kind": active.kind,
            "id": study_id,
            "title": active.title,
            "folder": folder_name + "/",
        },
        "next_actions": next_actions,
        "blockers": [],
    }


def add_history_entry(state: dict[str, Any], key: str, text: str, limit: int) -> None:
    value = (text or "").strip()
    if not value:
        return

    context = state.setdefault("context", {})
    history = context.setdefault(key, [])
    history.append(
        {
            "at": now_iso(),
            "text": value,
        }
    )
    context[key] = history[-limit:]


def recent_files_snapshot(limit: int = MAX_RECENT_FILES) -> list[str]:
    ignored_dirs = {".git", "Blender", "__pycache__", ".tmp", "tmp"}
    candidates: list[tuple[float, Path]] = []

    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue

        rel_parts = path.relative_to(ROOT).parts
        if any(part in ignored_dirs for part in rel_parts):
            continue

        try:
            mtime = path.stat().st_mtime
        except OSError:
            continue

        candidates.append((mtime, path))

    candidates.sort(key=lambda item: item[0], reverse=True)

    recent: list[str] = []
    for _, path in candidates:
        relative = str(path.relative_to(ROOT))
        if relative == str(STATE_PATH.relative_to(ROOT)):
            continue
        recent.append(relative)
        if len(recent) >= limit:
            break

    return recent


def infer_learning_hint(studies: list[update_progress.Study]) -> str:
    bonus = next((s for s in studies if s.kind == "bonus" and s.done < s.total), None)
    if bonus is not None and bonus.missing:
        return f"Likely recent focus: Bonus Study {bonus.bonus_index or ''} ({bonus.title}) — next missing: {bonus.missing[0]}.".replace("  ", " ")

    active = next((s for s in studies if s.done < s.total), None)
    if active is not None and active.missing:
        return f"Likely recent focus: {active.title} — next missing: {active.missing[0]}."

    return "No explicit learning focus note yet."


def progress_delta(previous: dict[str, Any], current: dict[str, Any]) -> str:
    prev_done = int(previous.get("overall_tasks_done", 0))
    curr_done = int(current.get("overall_tasks_done", 0))
    delta = curr_done - prev_done
    if delta > 0:
        return f"{delta} task(s) completed since your previous recap."
    if delta < 0:
        return "Task totals changed (likely checklist edits)."
    return "No checklist delta since your previous recap."


def trim_words(text: str, max_words: int) -> str:
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words]).rstrip() + " …"


def render_now_recap(
    state: dict[str, Any],
    status: dict[str, Any],
    focus: dict[str, Any],
    studies: list[update_progress.Study],
    max_words: int,
    max_bullets: int,
) -> str:
    phase_items = status.get("phase_summary", [])[:3]
    phase_line = "; ".join(
        f"{item['phase']}: {item['done']}/{item['total']} ({item['percent']}%)"
        for item in phase_items
    )

    active = focus["active_study"]
    active_label = f"{active.get('title', 'n/a')} ({focus.get('active_phase', 'n/a')})"

    context = state.get("context", {})
    chat = state.get("chat", {})

    latest_learning = (context.get("learning_history") or [])[-1]["text"] if context.get("learning_history") else infer_learning_hint(studies)
    latest_chat = (context.get("chat_history") or [])[-1]["text"] if context.get("chat_history") else "No chat-focus note saved yet."
    latest_workflow = (context.get("workflow_history") or [])[-1]["text"] if context.get("workflow_history") else "No workflow note saved yet."
    recent_files = context.get("recent_files") or []
    recent_files_line = ", ".join(recent_files[:4]) if recent_files else "none"

    bullets = [
        f"Where you are: {status['overall_tasks_done']}/{status['overall_tasks_total']} tasks complete ({status['overall_percent']}%), {status['studies_complete']}/{status['studies_total']} studies fully complete.",
        f"By phase: {phase_line or 'No phase data yet.'}",
        f"Current focus: {active_label}",
        f"Last learning focus: {latest_learning}",
        f"Last chat focus: {latest_chat}",
        f"What changed: {progress_delta(state.get('status', {}), status)}",
    ]

    next_actions = focus.get("next_actions", [])[:3]
    for idx, action in enumerate(next_actions, start=1):
        bullets.append(f"Next {idx}: {action}")

    blockers = focus.get("blockers", [])
    if blockers:
        bullets.append(f"Blocker: {blockers[0]}")
    else:
        bullets.append("Blocker: none logged.")

    bullets.append(f"Workflow exploration (secondary): {latest_workflow}")
    bullets.append(f"Recent edits snapshot: {recent_files_line}")

    last_thread = (chat.get("last_thread") or "").strip()
    resume_instruction = (chat.get("resume_instruction") or "").strip()
    if last_thread:
        bullets.append(f"Resume last chat thread: {last_thread}")
        if resume_instruction:
            bullets.append(f"Thread resume hint: {resume_instruction}")
        else:
            bullets.append("Thread resume hint: type 'resume thread' and mention this thread id/title.")

    bullets = bullets[:max_bullets]

    lines = [
        "# Resume Recap",
        "",
        f"Generated: {now_iso()}",
        "",
        "## Where we left off",
    ]
    lines.extend(f"- {b}" for b in bullets)
    lines.extend(
        [
            "",
            "## Weekly / Monthly retention",
            "- Weekly memory is compressed and kept to last 8 entries.",
            "- Monthly memory is consolidated and kept to last 6 entries.",
        ]
    )

    return trim_words("\n".join(lines), max_words)


def update_rolling_summary(state: dict[str, Any], recap: str) -> None:
    weekly = state.get("retention", {}).get("weekly", [])
    monthly = state.get("retention", {}).get("monthly", [])
    latest_week = weekly[-1]["week_id"] if weekly else "none"
    latest_month = monthly[-1]["month_id"] if monthly else "none"

    recap_body = recap.splitlines()
    if recap_body and recap_body[0].strip() == "# Resume Recap":
        recap_body = recap_body[1:]

    content = "\n".join(
        [
            "# Rolling Summary",
            "",
            "\n".join(recap_body).lstrip(),
            "",
            "## Retention pointers",
            f"- Latest weekly entry: {latest_week}",
            f"- Latest monthly entry: {latest_month}",
        ]
    )
    ROLLING_PATH.parent.mkdir(parents=True, exist_ok=True)
    ROLLING_PATH.write_text(content + "\n")


def add_weekly_entry(state: dict[str, Any], status: dict[str, Any], focus: dict[str, Any], max_words: int) -> str:
    today = datetime.now(timezone.utc)
    week_id = f"{today.isocalendar().year}-W{today.isocalendar().week:02d}"

    summary = (
        f"Week snapshot: {status['overall_tasks_done']}/{status['overall_tasks_total']} tasks complete "
        f"({status['overall_percent']}%). Active focus: {focus['active_study'].get('title', 'n/a')}"
    )
    summary = trim_words(summary, max_words)

    entry = {
        "week_id": week_id,
        "summary": summary,
        "wins": [focus.get("next_actions", ["Keep momentum with current study."])[0]],
        "carry_forwards": focus.get("next_actions", [])[:5],
        "dropped_items": [],
    }

    weekly = state.setdefault("retention", {}).setdefault("weekly", [])
    weekly = [item for item in weekly if item.get("week_id") != week_id]
    weekly.append(entry)
    state["retention"]["weekly"] = weekly[-8:]

    return f"Weekly summary updated for {week_id}."


def add_monthly_entry(state: dict[str, Any], status: dict[str, Any], focus: dict[str, Any], max_words: int) -> str:
    today = datetime.now(timezone.utc)
    month_id = f"{today.year}-{today.month:02d}"

    summary = (
        f"Monthly snapshot: {status['overall_tasks_done']}/{status['overall_tasks_total']} tasks complete "
        f"({status['overall_percent']}%), {status['studies_complete']}/{status['studies_total']} studies fully complete."
    )
    summary = trim_words(summary, max_words)

    entry = {
        "month_id": month_id,
        "summary": summary,
        "theme": focus.get("active_phase", "Phase focus"),
        "completed": [
            f"{status['overall_tasks_done']} tasks marked complete",
        ],
        "next_month_priorities": focus.get("next_actions", [])[:3],
    }

    monthly = state.setdefault("retention", {}).setdefault("monthly", [])
    monthly = [item for item in monthly if item.get("month_id") != month_id]
    monthly.append(entry)
    state["retention"]["monthly"] = monthly[-6:]

    return f"Monthly summary updated for {month_id}."


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a manual resume recap and maintain weekly/monthly memory.",
    )
    parser.add_argument(
        "--mode",
        choices=["now", "weekly", "monthly"],
        default="now",
        help="Run mode: immediate recap, weekly compression, or monthly consolidation.",
    )
    parser.add_argument("--max-words", type=int, default=220, help="Max words for recap text.")
    parser.add_argument("--max-bullets", type=int, default=12, help="Max bullets in recap sections.")
    parser.add_argument(
        "--learning-note",
        default="",
        help="Short note about what you were learning/studying/editing in the last session.",
    )
    parser.add_argument(
        "--workflow-note",
        default="",
        help="Short note about workflow automation ideas or implementation progress.",
    )
    parser.add_argument(
        "--chat-note",
        default="",
        help="Short note about key discussion topic from the previous chat session.",
    )
    parser.add_argument(
        "--set-thread",
        default="",
        help="Last chat thread id/title to surface in the recap.",
    )
    parser.add_argument(
        "--thread-hint",
        default="",
        help="Optional instruction for how to resume the thread in chat.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    state = load_state()

    studies = update_progress.parse_progress((ROOT / "PROGRESS.md").read_text())
    status = build_status(studies)
    focus = detect_focus(studies)

    add_history_entry(state, "learning_history", args.learning_note, MAX_LEARNING_HISTORY)
    add_history_entry(state, "workflow_history", args.workflow_note, MAX_WORKFLOW_HISTORY)
    add_history_entry(state, "chat_history", args.chat_note, MAX_CHAT_HISTORY)

    state.setdefault("context", {})["recent_files"] = recent_files_snapshot()

    if args.set_thread.strip():
        state.setdefault("chat", {})["last_thread"] = args.set_thread.strip()
    if args.thread_hint.strip():
        state.setdefault("chat", {})["resume_instruction"] = args.thread_hint.strip()

    if args.mode == "now":
        recap = render_now_recap(state, status, focus, studies, args.max_words, args.max_bullets)
        RESUME_PATH.parent.mkdir(parents=True, exist_ok=True)
        RESUME_PATH.write_text(recap + "\n")
        update_rolling_summary(state, recap)
        message = f"Resume recap written to {RESUME_PATH.relative_to(ROOT)}"
    elif args.mode == "weekly":
        message = add_weekly_entry(state, status, focus, max_words=min(args.max_words, 300))
    else:
        message = add_monthly_entry(state, status, focus, max_words=min(args.max_words, 500))

    state["resume"] = {
        "last_run_at": now_iso(),
        "last_mode": args.mode,
        "confidence": 0.85,
    }
    state["status"] = status
    state["focus"] = focus
    save_state(state)

    print(message)
    if args.mode == "now":
        print(recap)


if __name__ == "__main__":
    main()
