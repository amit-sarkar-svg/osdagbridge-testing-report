# All issues and bugs — OsdagBridge (plate girder, dev @ d74f56d)

**Mandate:** every substantiated finding listed with an ID and exactly one tier (T1–T9). Nothing silently dropped. No T3/T7 presented as confirmed; no invented evidence.

**Exclusions from "new":** #96 — `.osi` load skips `material.*` validation (filed earlier by this effort; https://github.com/Nidhikhare12/OsdagBridge/issues/96). Do not re-report as new.

## Summary counts
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

## Detailed entries

### P1-001 — `osdag_core` metadata declares bogus `sqlite` dependency (T5)
- **Tier:** T5 (Installation or environment blocker)
- **Filed:** [Nidhikhare12/OsdagBridge#98](https://github.com/Nidhikhare12/OsdagBridge/issues/98) (open, 2026-11-15) — draft: `notes/issue_drafts/06_osdag_core_bogus_sqlite_dependency.md`
- **Area:** Phase 1 — packaging/dependencies (installed dependency metadata)
- **Duplicate check:** full-body/title search via `scripts/search_issues.py` over `notes/issues_raw.json` (`evidence/logs/dupcheck_phase1_all.txt`): keywords `sqlite`, `osdag_core` — hits are #20/#42 (SQLite DB usage in design), unrelated to `osdag_core` pip metadata declaring a `sqlite` distribution. **No duplicate found.**
- **Evidence:** `evidence/logs/phase1_installed_meta.txt` (`osdag_core 0.0.0`): `Requires-Dist: ['pylatex', 'numpy', 'PyYaml', 'Click', 'pandas', 'sqlite', 'PySide6']`. `tests/test_phase1_packaging.py::test_osdag_core_declares_bogus_sqlite_dep` PASS. `pip index versions sqlite` → no matching distribution (stdlib module is `sqlite3`).
- **Expected vs actual:** dependency metadata should reference installable distributions; **actual:** declares `sqlite`, a non-installable/bogus distribution name that can break dependency resolution in clean environments.
- **Notes:** observed in installed `osdag_core` metadata in `osdagbridge-env` (not OsdagBridge source).

### P1-002 — `pyproject.toml` runtime dependencies omit required/used packages and include unused `pydantic` (T5)
- **Tier:** T5 (Installation or environment blocker)
- **Filed:** [Nidhikhare12/OsdagBridge#99](https://github.com/Nidhikhare12/OsdagBridge/issues/99) (open, 2026-11-15) — draft: `notes/issue_drafts/07_pyproject_missing_runtime_dependencies.md`
- **Area:** Phase 1 — `pyproject.toml` vs real imports/usage
- **Duplicate check:** full-body/title search (`evidence/logs/dupcheck_phase1_all.txt`): `pyproject` no match; `PySide6` only #25 (font fallback, unrelated); `pydantic` no match; `dependency` only #87 (seismic call-order, unrelated). **No duplicate found.**
- **Evidence (declared):** `OsdagBridge/pyproject.toml` deps = `[scipy>=1.10.1, fiona, shapely, pydantic>=2.0, matplotlib>=3.5, openseespy>=3.2.2.6, opsvis>=1.0, xarray]`. **Used/missing from pyproject (file:line examples, `evidence/logs/phase1_p1_002_proof.txt`):** PySide6 — `src/osdagbridge/desktop/ui/cad_3d.py:12` `from PySide6.QtWidgets import (` (185 imports total, `phase1_imports_clean.txt`); numpy — `src/ospgrillage/mesh.py:10` `import numpy as np`; osdag_core — `src/osdagbridge/core/utils/connect.py:31` `from osdag_core.cli import _get_output_dictionary`; yaml usage — `src/osdagbridge/desktop/ui/template_page.py:812` `yaml.dump(...)`, `:839` `yaml.safe_load(f)`; navcube — `src/osdagbridge/desktop/ui/utils/custom_3dviewer.py:13` `from navcube import NavCubeOverlay, NavCubeStyle`; OCC — `src/osdagbridge/core/bridge_types/plate_girder/cad_generator.py:26` `from OCC.Core.Quantity import ...`; plotly — `src/osdagbridge/core/bridge_types/plate_girder/plots_widget.py:2` `import plotly.graph_objects as go`; ifcopenshell — `src/osdagbridge/core/ifc_export_bridge/bridge_ifc_generator.py:7` `import ifcopenshell`; openpyxl — `src/osdagbridge/desktop/ui/dialogs/generate_results_dialog.py:1` `import openpyxl`; pandas — `src/osdagbridge/core/utils/codes/is800_2007.py:12` `import pandas as pd`. **Declared but not imported in `src`:** `pydantic` — `grep -rn "pydantic" src` returns only `src/osdagbridge.egg-info/*` (no source imports). README `README.md:90` instructs `pip install -e .`.
- **Expected vs actual:** declared runtime deps should cover packages required to import/run module features; **actual:** multiple used packages are omitted while `pydantic` is declared without observed use in `src`, so `pip install -e .` alone is insufficient as documented.
- **Notes:** some omissions are feature-specific (desktop/IFC/plots/export) but are direct source imports; `pylatex` not directly imported in `src` (not claimed).

### P1-003 — Inconsistent dependency declarations across `pyproject.toml`, `requirements.txt`, `environment.yml` (T6)
- **Tier:** T6 (Documentation/naming/packaging wording-consistency)
- **Area:** Phase 1 — packaging files consistency
- **Duplicate check:** full-body/title search (`evidence/logs/dupcheck_phase1_all.txt`): `requirements` no match; `environment.yml` appears only as environment context in unrelated issues (#25,#48,#64-#70,#84). **No duplicate found.**
- **Evidence:** `pyproject.toml` `[scipy,fiona,shapely,pydantic,matplotlib,openseespy,opsvis,xarray]`; `requirements.txt` `PySide6>=6.5.0,<=6.9.3,numpy,scipy,fiona,shapely,pydantic,xarray,ifcopenshell,openpyxl` (omits e.g. matplotlib/openseespy/opsvis/osdag_core/yaml/navcube/OCC/plotly/pandas); `environment.yml` uses `osdag::osdag` and pip-installs `openseespy,opsvis,-e .`.
- **Expected vs actual:** manifests should be consistent and aligned with real requirements; **actual:** three manifests disagree.

### P1-004 — README documents CLI commands that the stub CLI ignores (T6)
- **Tier:** T6 (Documentation/usage wording vs behavior)
- **Area:** Phase 1 — README & CLI entry point
- **Duplicate check:** full-body/title search (`evidence/logs/dupcheck_phase1_all.txt`): `README` no match; `CLI` hits refer to UI "click"/actions, not `osdagbridge-cli`. **No duplicate found.**
- **Evidence:** `README.md` shows `osdagbridge analyze project.yaml --solver native` and `osdagbridge report project.yaml report.pdf`. Actual (`evidence/logs/phase1_entrypoints.txt`): `osdagbridge-cli --help` and `osdagbridge-cli analyze project.yaml` both print `osdagbridge CLI (stub)` (exit 0). `src/osdagbridge/cli/__main__.py:4-6`: `def main(): print("osdagbridge CLI (stub)")`. `tests/test_phase1_packaging.py::test_cli_stub_ignores_args` PASS.
- **Expected vs actual:** documented CLI usage should work or be marked unimplemented; **actual:** CLI stub ignores args/help.

### P1-005 — `examples/plate_girder/verification_case_01.yaml` and `02` are empty placeholders (T6)
- **Tier:** T6 (Documentation/example content)
- **Area:** Phase 1 — examples
- **Duplicate check:** full-body/title search (`evidence/logs/dupcheck_phase1_all.txt`): `example`/`verification` hits unrelated to these shipped files. **No duplicate found.**
- **Evidence:** `evidence/logs/phase1_examples.txt`: both load as `None`/no keys, `validate_osi_inputs` → `is_valid=False`, errors `['File does not contain a valid input dictionary.']`. `tests/test_phase1_packaging.py::test_examples_parse_and_validate` PASS.
- **Expected vs actual:** verification examples should be loadable/meaningful; **actual:** empty/comment-only placeholders that fail validation.

### P1-006 — `example_basic.yaml` uses non-real keys yet passes `validate_osi_inputs` vacuously (T7)
- **Tier:** T7 (Oddity that might be intended)
- **Area:** Phase 1 — examples vs OSI validator behavior
- **Duplicate check:** full-body/title search (`evidence/logs/dupcheck_phase1_all.txt`): `example`/`yaml` hits relate to load/validation bugs (#19,#67,#69,#88), not this shipped example's placeholder schema. **No duplicate found.**
- **Evidence:** `evidence/logs/phase1_examples.txt`: top-level key `['project']`, no real dotted keys (`geometry.span`/`geometry.carriageway_width`/`geometry.skew_angle`), `validate_osi_inputs` → `is_valid=True, errors=[], warnings=[]`. `tests/test_phase1_packaging.py::test_examples_parse_and_validate` PASS. Validator polices only *present* known keys and does not require basic inputs at load.
- **Expected vs actual:** an illustrative example would typically use real dotted input keys; **actual:** placeholder schema (`project.span_m`) passes loader validation vacuously. May be intentional tolerance, but misleading.

### P1-007 — Web entry point is stubbed; desktop-parity (input dict/defaults/validation) cannot be tested (T9)
- **Tier:** T9 (Could not test)
- **Area:** Phase 1 — web entry point parity
- **Duplicate check:** not applicable (no parity claim to label duplicate).
- **Evidence:** `evidence/logs/phase1_entrypoints.txt`: `web/backend/manage.py` contains only a stub print; `web/frontend/package.json` minimal (`name`/`version` 0.0.0); no runnable backend/frontend implementing input dict/defaults/validation found.
- **What blocked:** absence of a functional web implementation prevents any meaningful comparison of input dict construction, defaults, or validation against the desktop UI.

### P1-008 — `pyproject.toml` declares console entry points for desktop and CLI (T8)
- **Tier:** T8 (Checked and correct)
- **Area:** Phase 1 — packaging metadata
- **Evidence:** `OsdagBridge/pyproject.toml` `[project.scripts]`: `osdagbridge-cli = "osdagbridge.cli.__main__:main"`, `osdagbridge = "osdagbridge.desktop.__main__:main"`; `osdagbridge-cli` resolves and runs in env (prints stub) per `evidence/logs/phase1_entrypoints.txt`.

### P1-009 — Core packages import successfully in `osdagbridge-env` (T8)
- **Tier:** T8 (Checked and correct)
- **Area:** Phase 1 — environment sanity
- **Evidence:** Phase 0/state check: `python -c "import osdagbridge, osdag_core"` → `ok`. `tests/test_phase1_packaging.py` (4 passed) executed in `osdagbridge-env` using `osdagbridge` APIs.

### P2-001 — `InputDock.toggle_lock` dereferences `_additional_inputs_dialog` without None-guard (T3)
- **Tier:** T3 (Static finding, from reading code; not executed)
- **Filed:** [Nidhikhare12/OsdagBridge#97](https://github.com/Nidhikhare12/OsdagBridge/issues/97) (open, 2026-11-15) — draft: `notes/issue_drafts/01_unguarded_additional_inputs_dialog_lock.md`
- **Area:** Phase 2 — lock/unlock flow (UI)
- **Duplicate check:** full-body search `scripts/search_issues.py "_additional_inputs_dialog"` → no match (`evidence/logs/dupcheck_additional_dialog.txt`).
- **Evidence:** `OsdagBridge/src/osdagbridge/desktop/ui/docks/input_dock.py:856-859`:
  > `self.is_locked = not self.is_locked`
  > `# Update Additional Input State (Lock/Unlock)`
  > `self.parent._additional_inputs_dialog.lock(lock=self.is_locked)`
  `template_page.py` initializes lazily: `:124` `self._additional_inputs_dialog: AdditionalInputs | None = None`, created on demand in `_get_additional_inputs()` (`:440-447`), and other template_page uses guard `if self._additional_inputs_dialog is not None:` (`:454,615,862`). If lock/unlock is toggled before the dialog is ever instantiated, `self.parent._additional_inputs_dialog` is `None` → `AttributeError`.
- **Expected vs actual:** lock state change should be safe regardless of dialog lifecycle; **actual:** unguarded dereference assumes dialog exists.

### P2-002 — Cross-bracing/end-diaphragm custom material subkeys written but not consumed by design (T4, dup #43)
- **Tier:** T4 (Duplicate — **#43** "Cross-bracing and end-diaphragm custom grades are stored but unused in design")
- **Area:** Phase 2 — custom-material flow (girder/cross-bracing/end diaphragm)
- **Duplicate check:** relates to open #43; extra detail added below.
- **Evidence:** UI/priming writes member-prefixed fields via `MaterialPropertiesDialog` (`dialogs/material_properties.py:556-576` `_member_prefix()` returns `material.cross_bracing`/`material.end_diaphragm`; `:578-594` `get_export_fields()` remaps steel template keys to member prefix) and input_dock applies/reads them (`docks/input_dock.py:324-345,763-779,808`). `notes/ui_key_map.csv` shows `material.cross_bracing.{density,fy,fu,e,g,poisson,thermal}` and `material.end_diaphragm.{...}` referenced in core only at `osdagbridge/core/utils/common.py` (constant definitions), with no reads in `plategirderbridge.py`/`designer.py`/`analyser.py` (`evidence/logs/phase2_*` / grep: no `KEY_MATERIAL_CROSS_BRACING*` or `material.cross_bracing.*` design reads). Grade-name keys `material.cross_bracing`/`material.end_diaphragm` are read, but sub-properties are not used in the design pipeline.
- **Expected vs actual:** custom sub-properties should drive member material behavior; **actual:** stored/exported in input_dict but unused by design (matches #43).
- **Extra detail for comment:** enumerate the specific unused subkeys per member (density, fy, fu, e, g, poisson, thermal) and their UI write path.

### P2-003 — Girder custom density ignored in `_build_material_props` (T4, dup #20)
- **Tier:** T4 (Duplicate — **#20** "Custom steel density from UI/input_dict is ignored in _build_material_props")
- **Area:** Phase 2 — custom-material flow (girder) / core read
- **Duplicate check:** matches open #20.
- **Evidence:** `plategirderbridge.py:1175-1215` sets `rho = _lookup_material(steel_grade, "Density")` and on failure falls back to fixed `_DEFAULT_DENSITY` (78500.0 N/m³) without reading `KEY_MATERIAL_GIRDER_DENSITY`/`material.girder.density`; other custom props (E, v, Fy, Fu) do read `KEY_MATERIAL_GIRDER_*`. UI/validator/report reference the key (`notes/ui_key_map.csv`: `validator.py`, `reports/chap3.py`, `common.py`).
- **Expected vs actual:** custom girder density should be used when DB lookup fails; **actual:** hardcoded fallback (same as #20).
- **Extra detail for comment:** UI path writes `material.girder.density` (MaterialPropertiesDialog/input_dock priming) and validator/report consume it, but design material build does not.

### P2-004 — Deck custom density not consumed in design load path (T4, dup #41)
- **Tier:** T4 (Duplicate — **#41** "Custom deck density never reaches create_deck_load (always 25 kN/m³)")
- **Area:** Phase 2 — custom-material flow (deck)
- **Duplicate check:** `scripts/search_issues.py "deck density"` / `"create_deck_load"` → #41 (`evidence/logs/dupcheck_deck_density.txt`).
- **Evidence:** `material.deck.density` (`KEY_MATERIAL_DECK_DENSITY`) is defined/validated/reported (`core/utils/common.py:97`, `core/bridge_types/plate_girder/validator.py:134`, `core/reports/chap3.py:19,282`; `notes/ui_key_map.csv`) but no read in `plategirderbridge.py` design/build path found (grep). UI writes it via deck material dialog/priming.
- **Expected vs actual:** custom deck density should influence deck self-weight/load; **actual:** not passed through design load creation (per #41).
- **Extra detail for comment:** key is present in validator and report but absent from design consumption.

### P2-005 — OSI/UI load does not restore `_material_custom_fields` (T4, dup #19)
- **Tier:** T4 (Duplicate — **#19** "OSI load does not restore _material_custom_fields; Design re-primes custom grades from defaults")
- **Area:** Phase 2 — load/populate & custom-material state
- **Duplicate check:** matches open #19.
- **Evidence:** `docks/input_dock.py:1048-1083` `populate_from_dict()` replaces `parent.input_dict`, sets widget texts/combo selections (adds missing combo item), marks `is_require_field_changed` and emits change — but does not restore `self._material_custom_fields` / prior-selection state. `_prime_material_inputs()` (`:324-345`) and custom handling rely on `_material_custom_fields` for custom selections.
- **Expected vs actual:** loading should restore custom material field state; **actual:** not restored (per #19).
- **Extra detail for comment:** `populate_from_dict` path and absence of `_material_custom_fields` restoration.

### P2-006 — UI schema typo: `section.additonal_geometry` (T6)
- **Tier:** T6 (Doc/typo/naming)
- **Area:** Phase 2 — UI field schema (`ui_fields.py`)
- **Duplicate check:** no matching existing issue (title/key typo search not present).
- **Evidence:** `evidence/logs/phase2_main_inputs.txt`: `ROW|section.additonal_geometry|title|...` (missing 'i' in "additional") in `FrontendData.input_values()`; internal section/title key, not a data key.
- **Expected vs actual:** consistent naming/spelling; **actual:** misspelled internal key `section.additonal_geometry`.

### P2-007 — Main UI data keys/defaults/dropdowns align with `BASIC_INPUT_DICT` and expected values (T8)
- **Tier:** T8 (Checked and correct)
- **Area:** Phase 2 — main input dock schema consistency
- **Duplicate check:** n/a.
- **Evidence:** `evidence/logs/phase2_main_inputs.txt`, `notes/ui_key_map.csv`: all 12 `BASIC_INPUT_DICT` data keys present in UI data keys; only extra UI key is `geometry.additional_btn` (button/action). Defaults match (`structure.type` Highway Bridge, include_median No, footpath None, design_mode Optimized, materials E 350A/M40). Combobox options consistent for main fields (structure type with 'Other' disabled, include_median No/Yes, footpath None/Single/Both, design_mode Optimized/Custom; materials from DB grades).

### P2-008 — Offscreen dock instantiation for dict read-back could not be completed (T9)
- **Tier:** T9 (Could not test)
- **Area:** Phase 2 — optional offscreen UI instantiation
- **Duplicate check:** n/a.
- **Evidence:** Attempt 1: `evidence/logs/phase2_offscreen_attempt1.txt` (exit 127, `timeout` unavailable). Attempt 2: `evidence/logs/phase2_offscreen_attempt2.txt` (exit 0 but `AttributeError: 'P' object has no attribute 'input_values'` at `docks/input_dock.py:92` inside `InputDock.__init__` with minimal harness). Stopped after 2 attempts per rules.
- **What blocked:** harness incompatibility/time constraints; dict read-back via live dock instantiation not achieved, so affected checks remained static (T3).
