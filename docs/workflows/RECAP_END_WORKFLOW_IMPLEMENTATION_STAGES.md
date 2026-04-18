# Workflow Enhancement Implementation Stages (Recap + End Commands)

This is the detailed execution document for the 7-stage workflow-enhancement plan focused on recap and end-session commands.

Use this file as the canonical reference when generating stage-specific Codex prompts, review checklists, and verification gates.

## Global operating rules

- One stage at a time.
- Manual git commit only (repo owner).
- Alias-first command UX is the long-term default.
- At each stage: implement → run checks → review output → iterate → commit.
- Do not proceed to next stage until acceptance criteria are met.

## Stage 1 — Tracking policy baseline

Checkpoint label: `chore/policy-baseline-tracking-rules`

### Tasks
- Confirm `STATE.json` remains tracked.
- Keep recap sample files tracked:
  - `docs/status/RESUME.md`
  - `docs/status/ROLLING_SUMMARY.md`
- Confirm `.gitignore` does not exclude canonical workflow state/docs/scripts.
- Document tracking policy in workflow docs.

### Tracking policy
- `STATE.json` is canonical workflow state and should stay versioned.
- `docs/status/RESUME.md` and `docs/status/ROLLING_SUMMARY.md` are canonical recap samples and should stay versioned.
- Workflow docs under `docs/workflows/` and workflow scripts under `scripts/` are canonical repo files and should stay versioned.
- `.gitignore` should be limited to local scratch files, caches, and large practice assets; it should not hide canonical workflow state, docs, status samples, or scripts.

### Checks
- Run:
  - `python3 scripts/update_progress.py`
  - `python3 scripts/resume_now.py --mode now`
- Verify generated outputs exist and are readable.
- Verify git status shows intended tracked files.

### Acceptance criteria
- Tracking policy is explicit in docs.
- Recap scripts run without errors.
- No accidental ignore rule blocks canonical files.

---

## Stage 2 — Progress/scoreboard hardening

Checkpoint label: `feat/progress-scoreboard-hardening`

### Tasks
- Validate parser behavior for:
  - numbered studies
  - bonus studies
  - phase assignment
  - missing-task extraction
- Ensure README scoreboard update is deterministic and idempotent.
- Improve parser resilience for minor formatting drift in `PROGRESS.md`.

### Checks
- Run `python3 scripts/update_progress.py` twice.
- Confirm second run introduces no additional changes.
- Confirm scoreboard table values match checklist counts.

### Acceptance criteria
- Parser handles current structure reliably.
- Scoreboard refresh is repeatable with stable output.

---

## Stage 3 — Study scaffolding robustness

Checkpoint label: `feat/study-scaffold-reliability`

### Tasks
- Harden `scripts/add_study.py` edge cases:
  - duplicate number protection
  - title slug cleanup
  - dry-run consistency
  - no-folder mode behavior
- Ensure generated progress blocks follow parser-friendly format.
- Ensure template population stays correct.

### Checks
- Run dry-run for several title formats.
- Verify no file mutation during dry-run.
- Add one controlled test study in a safe way (if needed), then validate parser/render.

### Acceptance criteria
- Scaffolding commands are predictable.
- New entries do not break scoreboard parsing.

---

## Stage 4 — Recap memory contract

Checkpoint label: `feat/resume-memory-contract`

### Tasks
- Stabilize `resume_now.py` data contract for:
  - `STATE.json`
  - `RESUME.md`
  - `ROLLING_SUMMARY.md`
- Keep recap concise but structured (status/focus/next/context/thread hint).
- Enforce weekly/monthly retention windows.
- Keep learning context higher priority than workflow context.
- Add explicit note for dual-thread requirement (planning thread + implementation thread) for later implementation.

### Checks
- Run:
  - `python3 scripts/resume_now.py --mode now`
  - `python3 scripts/resume_now.py --mode weekly`
  - `python3 scripts/resume_now.py --mode monthly`
- Validate state updates and retention caps.
- Validate recap readability in markdown preview.

### Acceptance criteria
- All three modes work reliably.
- State schema and recap output are stable and understandable.

---

## Stage 5 — Alias wrapper (default skill)

Checkpoint label: `feat/alias-command-wrapper`

### Tasks
- Add wrapper entrypoint for short commands (e.g., `resume`, `weekly`, `monthly`, `note`, `end`).
- Keep existing scripts as backend implementations.
- Add alias mapping documentation and examples.
- Record standing preference: always prefer alias-first command access.

### Checks
- Validate each alias resolves to intended backend command.
- Validate argument forwarding for notes/thread hints.
- Validate failure/help output is clear.

### Acceptance criteria
- User can run core workflow with short alias-style commands.
- Alias behavior is documented and stable.

---

## Stage 6 — End-of-day + forget-safe fallback

Checkpoint label: `feat/end-session-and-autocatchup`

### Tasks
- Add end-session command that runs maintenance steps in sequence:
  - progress refresh
  - recap update
  - optional weekly/monthly trigger (policy-based)
- Generate EOD summary artifact and user checklist.
- Checklist should include human-maintained items (commit, thread rename, etc.).
- Add fallback auto-catchup behavior for missed end command (next-session safety snapshot).

### Checks
- Run end-session flow and verify artifacts/checklist output.
- Simulate missed end-session and verify fallback capture occurs.
- Verify no destructive behavior.

### Acceptance criteria
- End workflow is actionable and reliable.
- Forget-safe fallback preserves enough context to resume.

---

## Stage 7 — Readability + governance docs finalization

Checkpoint label: `docs/operating-cadence-and-governance`

### Tasks
- Finalize canonical docs and remove ambiguity/duplication.
- Document architecture, command surface, and maintenance cadence.
- Ensure all docs consistently reference stage gates and review loops.
- Document dual-thread behavior requirement in finalized workflow docs.

### Checks
- Read-through consistency pass across:
  - `README.md`
  - `PROGRESS.md`
  - `docs/README.md`
  - `docs/workflows/RESUME.md`
  - roadmap docs
- Verify links and instructions are coherent.

### Acceptance criteria
- Documentation is complete and operationally clear.
- Future Codex prompts can be generated directly from docs with minimal thread dependence.

---

## Final Operating Cadence

- Start a session with `python3 scripts/workflow_alias.py resume`.
- Update learning checkboxes in `PROGRESS.md`; refresh the scoreboard with `python3 scripts/update_progress.py` when needed.
- Preserve context during a session with `python3 scripts/workflow_alias.py note "..."`.
- End a work block with `python3 scripts/workflow_alias.py end`.
- Use `end --weekly` or `end --monthly` when retention compression is due.
- If `end` is missed, the next resume run writes `docs/status/FALLBACK_SNAPSHOT.md`.

## Command Surface

- Alias wrapper: `scripts/workflow_alias.py`
- End-session backend: `scripts/session.py`
- Recap backend: `scripts/resume_now.py`
- Progress scoreboard backend: `scripts/update_progress.py`
- Study scaffolding backend: `scripts/add_study.py`

Alias-first is the default for workflow use. Direct backend commands remain valid for verification, debugging, and compatibility.

## Governance

- Work one stage at a time.
- Repo owner performs manual commits and pushes.
- Each stage follows: implement, verify, review, then manual commit if approved.
- Keep learning roadmap docs separate from workflow implementation docs.
- Keep `PROGRESS.md` focused on scene-study learning progress.
- Maintain two chat tracks when possible:
  - Planning thread: roadmap choices, stage decisions, and review gates.
  - Implementation/Codex thread: code changes, verification, and handoff evidence.

---

## Stage review template (use before each manual commit)

- Stage goal completed? (yes/no)
- Non-goals unchanged? (yes/no)
- Files changed are in scope? (yes/no)
- Checks passed? (list commands and results)
- User reviewed outputs in markdown/terminal? (yes/no)
- Risks/known follow-ups recorded? (yes/no)
- Ready for manual commit? (yes/no)

## Prompt handoff snippet for Codex

Use this minimal block when starting a stage in Codex:

- Target stage: `<N>/<7>`
- Source of truth docs:
  - `docs/roadmap/PRODUCTIONDESIGN.md`
  - `docs/workflows/RECAP_END_WORKFLOW_IMPLEMENTATION_STAGES.md`
- Rules: one stage only, alias-first preference, manual commit by user, stop after verification for review.
