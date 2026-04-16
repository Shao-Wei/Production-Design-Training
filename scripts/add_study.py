#!/usr/bin/env python3
"""Create a new scene-study folder and add it to PROGRESS.md."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import update_progress


ROOT = Path(__file__).resolve().parents[1]
PROGRESS = ROOT / "PROGRESS.md"
TEMPLATE = ROOT / "docs" / "templates" / "Scene Study Template.md"

TASKS = [
    "Scene analysis",
    "Color / palette analysis",
    "Hand-drawn scene sketch",
    "Script analysis",
]


def slug_title(title: str) -> str:
    cleaned = re.sub(r'[\\/:*?"<>|]', "", title).strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned or "Untitled Scene"


def next_study_number() -> int:
    studies = update_progress.parse_progress(PROGRESS.read_text())
    if not studies:
        return 1
    return max(int(study.number) for study in studies) + 1


def study_exists(number: int) -> bool:
    studies = update_progress.parse_progress(PROGRESS.read_text())
    return any(int(study.number) == number for study in studies)


def progress_block(number: int, title: str, folder_name: str, phase: str) -> str:
    task_lines = "\n".join(f"- [ ] {task}" for task in TASKS)
    return f"""## Study #{number} - {title}

Phase: {phase}

Folder: `{folder_name}/`

{task_lines}

Notes:
- Add starting notes here.
"""


def create_study_file(folder: Path, number: int, title: str) -> Path:
    study_file = folder / f"{folder.name}.md"
    if study_file.exists():
        return study_file

    text = TEMPLATE.read_text()
    text = re.sub(
        r"^# Scene Study #.*$",
        f"# Scene Study #{number} - {title}",
        text,
        count=1,
        flags=re.MULTILINE,
    )
    study_file.write_text(text)
    return study_file


def add_study(number: int, title: str, phase: str, create_folder: bool) -> tuple[Path | None, Path | None]:
    if study_exists(number):
        raise SystemExit(f"Study #{number} already exists in PROGRESS.md.")

    clean_title = slug_title(title)
    folder_name = f"Scene Study #{number} {clean_title}"
    folder = ROOT / folder_name
    study_file: Path | None = None

    if create_folder:
        folder.mkdir(exist_ok=False)
        study_file = create_study_file(folder, number, title)

    with PROGRESS.open("a") as progress_file:
        progress_file.write("\n\n" + progress_block(number, title, folder_name, phase).rstrip() + "\n")

    update_progress.main()
    return folder if create_folder else None, study_file


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Add a new scene study to PROGRESS.md and refresh the README scoreboard.",
    )
    parser.add_argument(
        "title",
        nargs="+",
        help='Study title, for example: "Bathroom Scene, Parasite"',
    )
    parser.add_argument(
        "-n",
        "--number",
        type=int,
        help="Study number. Defaults to the next available number.",
    )
    parser.add_argument(
        "--no-folder",
        action="store_true",
        help="Only add the checklist block; do not create a folder or study file.",
    )
    parser.add_argument(
        "--phase",
        default="Phase 1",
        help='Study phase label. Defaults to "Phase 1".',
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview the study number, folder, and checklist without changing files.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    number = args.number or next_study_number()
    title = " ".join(args.title).strip()
    phase = args.phase.strip()

    if args.dry_run:
        clean_title = slug_title(title)
        folder_name = f"Scene Study #{number} {clean_title}"
        print(f"Would add Study #{number}: {title}")
        print(f"Would use phase: {phase}")
        print(f"Would use folder: {folder_name}/")
        print()
        print(progress_block(number, title, folder_name, phase).rstrip())
        return

    folder, study_file = add_study(number, title, phase, create_folder=not args.no_folder)

    print(f"Added Study #{number}: {title}")
    print(f"Phase: {phase}")
    if folder is not None:
        print(f"Created folder: {folder.relative_to(ROOT)}")
    if study_file is not None:
        print(f"Created study file: {study_file.relative_to(ROOT)}")
    print("Updated PROGRESS.md and README.md")


if __name__ == "__main__":
    main()
