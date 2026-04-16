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
    number: str
    title: str
    done: int
    total: int
    missing: list[str]

    @property
    def percent(self) -> int:
        if self.total == 0:
            return 0
        return round((self.done / self.total) * 100)

    @property
    def bar(self) -> str:
        filled = round((self.done / self.total) * 10) if self.total else 0
        return "#" * filled + "-" * (10 - filled)


HEADING_RE = re.compile(r"^## Study #(\d+)\s*-\s*(.+)$")
TASK_RE = re.compile(r"^- \[([ xX])\] (.+)$")


def parse_progress(text: str) -> list[Study]:
    studies: list[Study] = []
    current_number: str | None = None
    current_title: str | None = None
    tasks: list[tuple[bool, str]] = []

    def flush() -> None:
        if current_number is None or current_title is None:
            return
        total = len(tasks)
        done = sum(1 for checked, _ in tasks if checked)
        missing = [label for checked, label in tasks if not checked]
        studies.append(Study(current_number, current_title, done, total, missing))

    for line in text.splitlines():
        heading = HEADING_RE.match(line)
        if heading:
            flush()
            current_number = heading.group(1)
            current_title = heading.group(2).strip()
            tasks = []
            continue

        task = TASK_RE.match(line)
        if task and current_number is not None:
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

    lines = [
        f"**Overall:** {completed}/{total} tasks complete ({percent}%). "
        f"{complete_studies}/{len(studies)} studies fully complete.",
        "",
        "| Study | Progress | Score | Missing |",
        "|---|---:|---:|---|",
    ]

    for study in studies:
        missing = ", ".join(study.missing) if study.missing else "Complete"
        lines.append(
            f"| #{study.number} - {study.title} | `{study.bar}` | "
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
