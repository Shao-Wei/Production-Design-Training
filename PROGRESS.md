# Scene Study Progress

Edit this file when a study moves forward. GitHub renders these as task checkboxes, and the README scoreboard is generated from this page.

## Progress Commands

Start the next study:

```bash
python3 scripts/add_study.py "Scene Name, Film Name"
```

Preview the new study without changing files:

```bash
python3 scripts/add_study.py --dry-run "Scene Name, Film Name"
```

Force a specific study number:

```bash
python3 scripts/add_study.py --number 3 "Scene Name, Film Name"
```

Set a phase explicitly:

```bash
python3 scripts/add_study.py --phase "Phase 1" "Scene Name, Film Name"
```

Add only the checklist block, without creating a folder or study file:

```bash
python3 scripts/add_study.py --no-folder "Scene Name, Film Name"
```

Refresh the README scoreboard after editing checkboxes by hand:

```bash
python3 scripts/update_progress.py
```

On GitHub, the scoreboard refreshes automatically after changes to this file are pushed.

Phase 1 checklist:
- Scene analysis
- Color / palette analysis
- Hand-drawn scene sketch
- Script analysis

## Study #1 - K's Room, Blade Runner 2049

Phase: Phase 1

Folder: `Scene Study #1 K's Room, Bladerunner2049/`

- [x] Scene analysis
- [x] Color / palette analysis
- [x] Hand-drawn scene sketch
- [ ] Script analysis

Notes:
- Scene analysis is written in the study folder.
- Color / palette analysis exists as a `.kra` file.
- Hand sketch is done, but not uploaded here yet.
- Script PDF is uploaded; script analysis still needs to be written.

## Study #2 - March House, Little Women

Phase: Phase 1

Folder: `Scene Study #2 March House, Little Women/`

- [x] Scene analysis
- [ ] Color / palette analysis
- [ ] Hand-drawn scene sketch
- [ ] Script analysis

Notes:
- Scene analysis is written in the study folder.
- Update the remaining checkboxes as those artifacts are added.
