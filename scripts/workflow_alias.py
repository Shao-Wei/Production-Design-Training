#!/usr/bin/env python3
"""Short alias wrapper for workflow commands."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESUME_NOW = ROOT / "scripts" / "resume_now.py"

ALIASES = {
    "resume": "Generate the current resume recap.",
    "weekly": "Run weekly memory compression.",
    "monthly": "Run monthly memory consolidation.",
    "note": "Capture a quick learning note, or forward resume_now note flags.",
    "end": "Reserved for Stage 6 end-session flow.",
}


def print_help() -> None:
    print("Usage: python3 scripts/workflow_alias.py <alias> [args]")
    print()
    print("Aliases:")
    print("  resume [args]   -> python3 scripts/resume_now.py --mode now [args]")
    print("  weekly [args]   -> python3 scripts/resume_now.py --mode weekly [args]")
    print("  monthly [args]  -> python3 scripts/resume_now.py --mode monthly [args]")
    print("  note <text>     -> python3 scripts/resume_now.py --mode now --learning-note <text>")
    print("  note [flags]    -> python3 scripts/resume_now.py --mode now [flags]")
    print("  end             -> not available until Stage 6")
    print()
    print("Examples:")
    print("  python3 scripts/workflow_alias.py resume")
    print("  python3 scripts/workflow_alias.py weekly")
    print("  python3 scripts/workflow_alias.py note \"Reviewed K's room script cues\"")
    print("  python3 scripts/workflow_alias.py note --chat-note \"Discussed scene contrast\"")


def run_resume_now(mode: str, args: list[str]) -> int:
    command = [sys.executable, str(RESUME_NOW), "--mode", mode, *args]
    return subprocess.run(command, cwd=ROOT).returncode


def run_note(args: list[str]) -> int:
    if not args:
        print("error: note requires note text or resume_now note flags.", file=sys.stderr)
        print("Try: python3 scripts/workflow_alias.py note \"Focused on Study #1 script analysis\"", file=sys.stderr)
        return 2

    if any(arg.startswith("--") for arg in args):
        return run_resume_now("now", args)

    return run_resume_now("now", ["--learning-note", " ".join(args)])


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args or args[0] in {"-h", "--help", "help"}:
        print_help()
        return 0

    alias, rest = args[0], args[1:]

    if alias == "resume":
        return run_resume_now("now", rest)
    if alias == "weekly":
        return run_resume_now("weekly", rest)
    if alias == "monthly":
        return run_resume_now("monthly", rest)
    if alias == "note":
        return run_note(rest)
    if alias == "end":
        print("The 'end' alias is not available yet. It is reserved for Stage 6 end-session flow.")
        return 2

    print(f"error: unknown alias '{alias}'.", file=sys.stderr)
    print(f"Known aliases: {', '.join(ALIASES)}", file=sys.stderr)
    print("Run with --help for examples.", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
