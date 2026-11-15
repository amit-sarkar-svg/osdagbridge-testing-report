# QA STATE — OsdagBridge (plate girder, branch dev)

## Environment & paths
- Testing repo (write here): `/Users/macbook/Projects/osdagbridge-testing-report`
- OsdagBridge clone (READ-ONLY): `/Users/macbook/Projects/OsdagBridge` (branch `dev`, commit `d74f56d`)
- Conda env: `osdagbridge-env` (Python 3.12.16, osdagbridge/osdag_core import OK). pdflatex installed.
- Baseline input: `test_cases/baseline.osi` **MISSING** (blocks Phases 4, 5). Phases 1–3 do not need it.

## Current phase
- **Phase 2 complete.** Next: Phase 3 (validation rule drift).

## What is done
- Phase 0: fetched all issues (open+closed, PRs skipped) via `gh api` → `notes/issues_raw.json` (96 items) and compact `notes/existing_issues.md` (40 issues: 39 open, 1 closed). Created `notes/all_issues_and_bugs.md`, `notes/STATE.md`, `notes/RULES.md`.
- Phase 1 (packaging/docs/entry points): compared manifests vs real imports/installed metadata, validated examples, checked CLI/web/README, added `tests/test_phase1_packaging.py` (4 passed). Logged P1-001..P1-009. Dup-check fix via `scripts/search_issues.py` full-body search — no T4 re-tier; refined P1-002 evidence.
- Pre-existing (retained): pytest suite (18 pass, 1 dup #88), pipeline scripts/probes, `notes/findings.md` F1–F4, issue **#96 filed** (excluded from "new").
- Phase 2 (UI→core data integrity, reading-first): built `notes/ui_key_map.csv` (39 rows: main inputs + material subkeys, core refs) and `evidence/logs/phase2_main_inputs.txt`; verified main UI keys/defaults/dropdowns vs `BASIC_INPUT_DICT` (`P2-007` T8). Traced custom-material/priming/load flows (input_dock, material_properties, template_page lifecycle) and lock/unlock — logged `P2-001` (T3, unguarded additional_inputs_dialog.lock), `P2-002..P2-005` (T4 dups #43/#20/#41/#19), `P2-006` (T6 schema typo). Offscreen dock instantiation attempted twice, not completed (`P2-008` T9). **Partial:** exhaustive dialog/additional_inputs-schema widget map and full unit-label/tooltip-vs-limit audit across all dialogs not completed this session (budget) — carry to Phase 3/targeted follow-up; core `validator.py`/`common.py` limits comparison deferred to Phase 3.

## What is next
- Phase 2: UI→core data integrity by reading — `desktop/ui/template_page.py`, `docks/input_dock.py`, other docks, `dialogs/*`. Grep keys/widgets, produce compact map `notes/ui_key_map.csv` (widget->key->where read in core). Check dead inputs, UI defaults vs `BASIC_INPUT_DICT`, unit labels/tooltips vs real limits, dropdowns vs `VALUES_*` in `common.py`, custom-material flow (`MATERIAL_CUSTOM_OPTION`) per component and what’s not written, lock/unlock/reset (stale fields/vars). Optional: try `QT_QPA_PLATFORM=offscreen` to instantiate docks/read dict (≤2 attempts) else mark T3. Append findings with IDs/tiers+evidence, update counts.

## Tier counts (new findings, this audit)
| Tier | Count |
|---|---:|
| T1 Confirmed bug | 0 |
| T2 Likely bug | 0 |
| T3 Static finding | 1 |
| T4 Duplicate | 4 |
| T5 Installation/env blocker | 2 |
| T6 Doc/typo/unit-label/wording | 4 |
| T7 Oddity, maybe intended | 1 |
| T8 Checked and correct | 3 |
| T9 Could not test | 2 |
| **Total** | **17** |

## Key facts learned
- Duplicate baseline: 40 issues (#18–#96). #96 excluded. Prior dups: F1→#88, F2→#20, F4→#19, Gs→#42, thermal→#92.
- `baseline.osi` missing; do not fabricate (blocks Phases 4,5).
- **P1 deps:** `osdag_core 0.0.0` Requires-Dist includes bogus `sqlite` (T5). `pyproject.toml` deps omit PySide6/numpy/osdag_core/PyYAML/navcube/OCC/plotly/ifcopenshell/openpyxl/pandas (and declares unused `pydantic`); manifests inconsistent (T5/T6). README `pip install -e .` insufficient as-is.
- **P1 CLI/examples/web:** `osdagbridge-cli` is a stub ignoring args/help despite README commands (T6). `verification_case_01/02.yaml` empty/invalid, `example_basic.yaml` uses non-real keys but passes `validate_osi_inputs` vacuously (T6/T7). Web backend/frontend stubbed → parity untestable (T9).
- Always search `notes/existing_issues.md` (+raw) by keyword/file before labeling new.
- **P2 UI integrity:** `notes/ui_key_map.csv` (main+material keys) built; main UI data keys/defaults aligned with `BASIC_INPUT_DICT` (T8). Findings: unguarded `input_dock.toggle_lock` → `additional_inputs_dialog.lock` on None (T3, `docks/input_dock.py:858`); CB/ED custom material subkeys written but not design-consumed (T4 #43), girder custom density fallback ignores input key (T4 #20), deck density not consumed in load path (T4 #41), `_material_custom_fields` not restored on load (T4 #19); schema typo `section.additonal_geometry` (T6). Offscreen read-back not completed (T9). Additional_inputs/dialog unit-label audit deferred.

## Evidence/log locations
- `evidence/logs/` (phase1: `phase1_imports_clean.txt`, `phase1_dep_grep.txt`, `phase1_installed_meta.txt`, `phase1_examples.txt`, `phase1_entrypoints.txt`, `phase1_pytest.txt`), `notes/issue_drafts/`
