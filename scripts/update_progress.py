#!/usr/bin/env python3
"""Update the README scene-study progress scoreboard from PROGRESS.md."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
PROGRESS = ROOT / "PROGRESS.md"

START = "<!-- progress:start -->"
END = "<!-- progress:end -->"


@dataclass
class Study:
    number: str | None
    title: str
    phase: str
    done: int
    total: int
    missing: list[str]
    kind: str = "study"
    bonus_index: str | None = None

    @property
    def percent(self) -> int:
        if self.total == 0:
            return 0
        return round((self.done / self.total) * 100)

    @property
    def bar(self) -> str:
        filled = round((self.done / self.total) * 10) if self.total else 0
        return "#" * filled + "-" * (10 - filled)

    @property
    def display_name(self) -> str:
        if self.kind == "bonus":
            index = f" {self.bonus_index}" if self.bonus_index else ""
            return f"Bonus{index} - {self.title}"
        return f"#{self.number} - {self.title}"


HEADING_RE = re.compile(r"^## Study #(\d+)\s*-\s*(.+)$")
BONUS_HEADING_RE = re.compile(r"^## Bonus Study(?:\s+([A-Z]+))?\s*-\s*(.+)$")
PHASE_RE = re.compile(r"^Phase:\s*(.+)$")
TASK_RE = re.compile(r"^- \[([ xX])\] (.+)$")


def number_to_letters(number: int) -> str:
    letters = ""
    while number:
        number, remainder = divmod(number - 1, 26)
        letters = chr(ord("A") + remainder) + letters
    return letters


def parse_progress(text: str) -> list[Study]:
    studies: list[Study] = []
    current_number: str | None = None
    current_title: str | None = None
    current_phase = "Phase 1"
    current_kind = "study"
    current_bonus_index: str | None = None
    bonus_count = 0
    tasks: list[tuple[bool, str]] = []

    def flush() -> None:
        if current_title is None:
            return
        total = len(tasks)
        done = sum(1 for checked, _ in tasks if checked)
        missing = [label for checked, label in tasks if not checked]
        studies.append(
            Study(
                current_number,
                current_title,
                current_phase,
                done,
                total,
                missing,
                current_kind,
                current_bonus_index,
            )
        )

    for line in text.splitlines():
        if line.startswith("## "):
            heading = HEADING_RE.match(line)
            if heading:
                flush()
                current_number = heading.group(1)
                current_title = heading.group(2).strip()
                current_phase = "Phase 1"
                current_kind = "study"
                current_bonus_index = None
                tasks = []
                continue

            bonus_heading = BONUS_HEADING_RE.match(line)
            if bonus_heading:
                flush()
                bonus_count += 1
                current_number = None
                current_bonus_index = bonus_heading.group(1) or number_to_letters(bonus_count)
                current_title = bonus_heading.group(2).strip()
                current_phase = "Phase 1 (Bonus Track)"
                current_kind = "bonus"
                tasks = []
                continue

            # Any other level-2 heading ends the current numbered study block.
            flush()
            current_number = None
            current_title = None
            current_phase = "Phase 1"
            current_kind = "study"
            current_bonus_index = None
            tasks = []
            continue

        phase = PHASE_RE.match(line)
        if phase and current_title is not None:
            current_phase = phase.group(1).strip()
            continue

        task = TASK_RE.match(line)
        if task and current_title is not None:
            tasks.append((task.group(1).lower() == "x", task.group(2).strip()))

    flush()
    return studies


def render_scoreboard(studies: list[Study]) -> str:
    if not studies:
        return "No scene studies found in `PROGRESS.md`."

    completed = sum(study.done for study in studies)
    total = sum(study.total for study in studies)
    percent = round((completed / total) * 100) if total else 0
    complete_studies = sum(1 for study in studies if study.total and study.done == study.total)
    phases = sorted({study.phase for study in studies})
    phase_summary = []

    for phase in phases:
        phase_done = sum(study.done for study in studies if study.phase == phase)
        phase_total = sum(study.total for study in studies if study.phase == phase)
        phase_percent = round((phase_done / phase_total) * 100) if phase_total else 0
        phase_summary.append(f"{phase}: {phase_done}/{phase_total} ({phase_percent}%)")

    lines = [
        f"**Overall:** {completed}/{total} tasks complete ({percent}%). "
        f"{complete_studies}/{len(studies)} studies fully complete.",
        f"**By phase:** {'; '.join(phase_summary)}.",
        "",
        "| Phase | Study | Progress | Score | Missing |",
        "|---|---|---:|---:|---|",
    ]

    for study in studies:
        missing = ", ".join(study.missing) if study.missing else "Complete"
        lines.append(
            f"| {study.phase} | {study.display_name} | `{study.bar}` | "
            f"{study.done}/{study.total} ({study.percent}%) | {missing} |"
        )

    lines.extend(
        [
            "",
            "Update checkboxes in `PROGRESS.md`, then run "
            "`python3 scripts/update_progress.py` to refresh this table. "
            "On GitHub, the included workflow refreshes it automatically after pushes to `PROGRESS.md`.",
        ]
    )
    return "\n".join(lines)


def update_readme(readme_text: str, scoreboard: str) -> str:
    block_re = re.compile(
        rf"{re.escape(START)}.*?{re.escape(END)}",
        re.DOTALL,
    )
    replacement = f"{START}\n{scoreboard}\n{END}"

    if block_re.search(readme_text):
        return block_re.sub(replacement, readme_text)

    marker = "## How to Use This Workspace"
    section = f"## Scene Study Scoreboard\n\n{replacement}\n\n"
    if marker in readme_text:
        return readme_text.replace(marker, section + marker, 1)

    return readme_text.rstrip() + "\n\n" + section


def main() -> None:
    studies = parse_progress(PROGRESS.read_text())
    scoreboard = render_scoreboard(studies)
    README.write_text(update_readme(README.read_text(), scoreboard))


if __name__ == "__main__":
    main()
