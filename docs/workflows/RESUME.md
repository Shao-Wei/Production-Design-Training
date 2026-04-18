# Resume Now Workflow

Use this workflow whenever you come back to the project and want a fast recap without loading full chat history.

## Command

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

The recap now includes:
- task scoreboard status and next actions
- last learning focus (what you were studying/editing)
- last chat focus + optional thread resume hint
- recent edit snapshot
- workflow exploration notes (secondary priority)

Then in chat, simply type:

```text
resume now
```

and paste `docs/status/RESUME.md` if needed.

## Retention Commands

Weekly compression:

```bash
python3 scripts/resume_now.py --mode weekly
```

Monthly consolidation:

```bash
python3 scripts/resume_now.py --mode monthly
```

## Brevity Policy

- Resume recap: up to 220 words, up to 12 bullets, 3 next actions, 1 blocker line.
- Weekly memory: keep latest 8 entries.
- Monthly memory: keep latest 6 entries.

## Suggested cadence

- Every session start: run `--mode now`.
- End of each week: run `--mode weekly`.
- End of each month: run `--mode monthly`.
