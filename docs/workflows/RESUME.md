# Resume Now Workflow

Use this workflow whenever you come back to the project and want a fast recap without loading full chat history.

## Command

Alias-first command access is the standing preference. Use the wrapper first:

```bash
python3 scripts/workflow_alias.py resume
```

Direct backend command:

```bash
python3 scripts/resume_now.py --mode now
```

Optional richer context capture:

```bash
python3 scripts/resume_now.py --mode now \
	--learning-note "Focused on Bonus Study A clip review and redesign questions" \
	--chat-note "Discussed emotional shift through gradual dissonance" \
	--workflow-note "Scoreboard/resume automation improvements to explore next" \
	--set-thread "Production Design thread - 2026-04-18" \
	--thread-hint "In chat, ask: resume thread Production Design thread - 2026-04-18"
```

This generates:
- `docs/status/RESUME.md` (session recap)
- `docs/status/ROLLING_SUMMARY.md` (rolling context view)
- `STATE.json` updates (compact machine-readable memory)

The recap contract keeps these sections stable:
- Status: task scoreboard and phase progress.
- Focus: current study and progress delta.
- Next: up to 3 next actions plus blocker line.
- Context: learning focus first, then chat focus, recent edits, and workflow notes as secondary context.
- Thread Hint: current thread reminder plus the dual-thread requirement.
- Weekly / Monthly retention: current retention windows.

Dual-thread requirement for later implementation:
- Planning thread: high-level roadmap, stage decisions, and review gates.
- Implementation thread: code changes, verification, and handoff evidence.
- Keep these separate when the workflow grows beyond the current single-thread manual command flow.

Then in chat, simply type:

```text
resume now
```

and paste `docs/status/RESUME.md` if needed.

## Retention Commands

Weekly compression:

```bash
python3 scripts/workflow_alias.py weekly
```

Monthly consolidation:

```bash
python3 scripts/workflow_alias.py monthly
```

Direct backend commands still work:

```bash
python3 scripts/resume_now.py --mode weekly
python3 scripts/resume_now.py --mode monthly
```

## Alias Map

- `resume` -> `python3 scripts/resume_now.py --mode now`
- `weekly` -> `python3 scripts/resume_now.py --mode weekly`
- `monthly` -> `python3 scripts/resume_now.py --mode monthly`
- `note "..."` -> `python3 scripts/resume_now.py --mode now --learning-note "..."`
- `note --learning-note "..." --chat-note "..." --workflow-note "..." --thread-hint "..."`
  forwards note and thread arguments to `resume_now.py --mode now`.
- `end` is reserved for Stage 6 and currently returns an explicit "not available yet" message.

Examples:

```bash
python3 scripts/workflow_alias.py resume
python3 scripts/workflow_alias.py weekly
python3 scripts/workflow_alias.py monthly
python3 scripts/workflow_alias.py note "Focused on Study #1 script analysis"
python3 scripts/workflow_alias.py note --chat-note "Discussed scene contrast"
python3 scripts/workflow_alias.py end
```

## Brevity Policy

- Resume recap: up to 220 words, up to 12 bullets, 3 next actions, 1 blocker line.
- Weekly memory: keep latest 8 entries.
- Monthly memory: keep latest 6 entries.

## Suggested cadence

- Every session start: run `--mode now`.
- End of each week: run `--mode weekly`.
- End of each month: run `--mode monthly`.
