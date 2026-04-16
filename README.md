# Production Design Study Project

A self-directed, long-term production design training workspace focused on scene analysis, visual storytelling, and practical environment design.

## Motivation & Goal

This project is built around one core idea: production design skill can be developed through consistent practice, even without a formal art school path.

The goal is to train:
- visual taste and observation
- story-first spatial thinking
- color and material sensitivity
- set/prop logic tied to character, class, and world
- communication through boards, notes, and renders

Instead of chasing perfect finished art, the project emphasizes a repeatable learning loop:

**study scenes → explain design choices → test alternatives → build your own scene packages**

## Study Roadmap (Overview)

The study path in this workspace combines long-range progression with weekly repeatable practice.

### Phase 1 — Eye Training & Habit (First 3 months)
- frequent scene breakdowns
- small Blender corner rebuilds
- quick hand sketching and material reference collection
- focus on finishing small studies consistently

### Phase 2 — Original Design Thinking (Months 4–9)
- move from recreation into original scene concepts
- build project packets (premise, character, mood board, color script, plan, render)
- practice contrast exercises (same room across different budgets/characters)

### Phase 3 — Multi-Set Story Worlds (Months 10–18)
- design connected environments for a short-film-style world
- incorporate script-to-space analysis
- think in art-department workflow terms, not only isolated images

### Phase 4 — Portfolio & Collaboration (Years 2–3)
- assemble short-film design packages
- improve speed, iteration, and revision quality
- collaborate with indie/student productions

### 8-Study Ladder Direction
The scene-selection roadmap emphasizes contrast learning across 8 categories:
- cold sparse domestic
- warm lived-in domestic
- class contrast
- period realism
- opulence/power spaces
- architecture-as-character
- institutional/procedural spaces
- thresholds/transition spaces

## Overall Workflow

A typical study cycle in this repo follows:

1. **Choose a scene** with clear spatial and emotional design value.
2. **Run scene analysis** using the template checklist (story, character, space, design language, realism).
3. **Do color study** (extract palette, build swatches, test controlled variants, justify changes by story impact).
4. **Optional script snapshot study** (short excerpt + annotation for space/prop/psychology cues).
5. **Build a spatial interpretation** (thumbnail/floor-plan thinking + Blender blockout).
6. **Develop materials/props/lighting** with a story-first lens.
7. **Write a short reflection**: what worked, what was learned, what to test next.

Recommended default production loop:

**story premise → reference board → design notes → thumbnails → floor plan → Blender blockout → materials/props → render → self-critique**

## Repository Organization

### Core guidance files
- `docs/roadmap/PRODUCTIONDESIGN.md`  
  Long-term training philosophy, phases, weekly systems, and skill priorities.

- `docs/roadmap/SCENECHOICE.md`  
  Comparative 8-study ladder for selecting scenes with intentional contrast.

- `docs/workflows/COLORSTUDY.md`  
  Detailed palette extraction and Photoshop variation workflow for production-design color thinking.

- `docs/workflows/SCRIPTSTUDY.md`  
  Practical approach for using short screenplay excerpts in scene analysis.

- `docs/workflows/VIDEOLIST.md`  
  Research/watch-source suggestions for set breakdowns and craft learning.

- `docs/templates/Scene Study Template.md`  
  Reusable checklist structure for each scene study write-up.

- `PROGRESS.md`  
  Simple checkbox tracker for each scene study and source for the README scoreboard.

### Scene study outputs
- `Scene Study #1 K's Room, Bladerunner2049/`  
  Completed sparse/cold anchor study, including notes and image workflow artifacts.

- `Scene Study #2 March House, Little Women/`  
  Warm/lived-in domestic contrast study.

### 3D practice assets
- `Blender/`  
  Blender files and material practice assets for environment studies.

## How to Use This Workspace

1. Start from `docs/roadmap/SCENECHOICE.md` to pick the next study type.
2. Run `python3 scripts/add_study.py "Scene Name, Film Name"` to create the next study folder and checklist.
3. Complete analysis notes first, then color/script/spatial exercises.
4. Store Blender iterations in `Blender/` or scene-specific subfolders.
5. Update `PROGRESS.md` as each study task is finished.
6. Keep each study focused and finishable; prioritize consistency over complexity.

## Current Progress Snapshot

See `PROGRESS.md` for the editable checklist.

## Scene Study Scoreboard

<!-- progress:start -->
**Overall:** 4/8 tasks complete (50%). 0/2 studies fully complete.
**By phase:** Phase 1: 4/8 (50%).

| Phase | Study | Progress | Score | Missing |
|---|---|---:|---:|---|
| Phase 1 | #1 - K's Room, Blade Runner 2049 | `########--` | 3/4 (75%) | Script analysis |
| Phase 1 | #2 - March House, Little Women | `##--------` | 1/4 (25%) | Color / palette analysis, Hand-drawn scene sketch, Script analysis |

Update checkboxes in `PROGRESS.md`, then run `python3 scripts/update_progress.py` to refresh this table. On GitHub, the included workflow refreshes it automatically after pushes to `PROGRESS.md`.
<!-- progress:end -->

---

This project is designed as an ongoing design apprenticeship with yourself: sustained, iterative, and story-centered.
