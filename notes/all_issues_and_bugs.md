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
- **Filed:** [Nidhikhare12/OsdagBridge#100](https://github.com/Nidhikhare12/OsdagBridge/issues/100) (open, 2026-11-15) — draft: `notes/issue_drafts/08_inconsistent_dependency_manifests.md`
- **Area:** Phase 1 — packaging files consistency
- **Duplicate check:** full-body/title search (`evidence/logs/dupcheck_phase1_all.txt`): `requirements` no match; `environment.yml` appears only as environment context in unrelated issues (#25,#48,#64-#70,#84). **No duplicate found.**
- **Evidence:** `pyproject.toml` `[scipy,fiona,shapely,pydantic,matplotlib,openseespy,opsvis,xarray]`; `requirements.txt` `PySide6>=6.5.0,<=6.9.3,numpy,scipy,fiona,shapely,pydantic,xarray,ifcopenshell,openpyxl` (omits e.g. matplotlib/openseespy/opsvis/osdag_core/yaml/navcube/OCC/plotly/pandas); `environment.yml` uses `osdag::osdag` and pip-installs `openseespy,opsvis,-e .`.
- **Expected vs actual:** manifests should be consistent and aligned with real requirements; **actual:** three manifests disagree.

### P1-004 — README documents CLI commands that the stub CLI ignores (T6)
- **Tier:** T6 (Documentation/usage wording vs behavior)
- **Filed:** [Nidhikhare12/OsdagBridge#101](https://github.com/Nidhikhare12/OsdagBridge/issues/101) (open, 2026-11-15) — draft: `notes/issue_drafts/09_readme_cli_commands_but_stub_ignores_args.md`
- **Area:** Phase 1 — README & CLI entry point
- **Duplicate check:** full-body/title search (`evidence/logs/dupcheck_phase1_all.txt`): `README` no match; `CLI` hits refer to UI "click"/actions, not `osdagbridge-cli`. **No duplicate found.**
- **Evidence:** `README.md` shows `osdagbridge analyze project.yaml --solver native` and `osdagbridge report project.yaml report.pdf`. Actual (`evidence/logs/phase1_entrypoints.txt`): `osdagbridge-cli --help` and `osdagbridge-cli analyze project.yaml` both print `osdagbridge CLI (stub)` (exit 0). `src/osdagbridge/cli/__main__.py:4-6`: `def main(): print("osdagbridge CLI (stub)")`. `tests/test_phase1_packaging.py::test_cli_stub_ignores_args` PASS.
- **Expected vs actual:** documented CLI usage should work or be marked unimplemented; **actual:** CLI stub ignores args/help.

### P1-005 — `examples/plate_girder/verification_case_01.yaml` and `02` are empty placeholders (T6)
- **Tier:** T6 (Documentation/example content)
- **Filed:** [Nidhikhare12/OsdagBridge#127](https://github.com/Nidhikhare12/OsdagBridge/issues/127) (open, 2026-11-17) — draft: `notes/issue_drafts/11_empty_verification_example_placeholders.md`
- **Area:** Phase 1 — examples
- **Duplicate check:** full-body/title search (`evidence/logs/dupcheck_phase1_all.txt`): `example`/`verification` hits unrelated to these shipped files. **No duplicate found.**
- **Evidence:** `evidence/logs/phase1_examples.txt`: both load as `None`/no keys, `validate_osi_inputs` → `is_valid=False`, errors `['File does not contain a valid input dictionary.']`. `tests/test_phase1_packaging.py::test_examples_parse_and_validate` PASS.
- **Expected vs actual:** verification examples should be loadable/meaningful; **actual:** empty/comment-only placeholders that fail validation.

### P1-006 — `example_basic.yaml` uses non-real keys yet passes `validate_osi_inputs` vacuously (T7)
- **Tier:** T7 (Oddity that might be intended)
- **Filed:** [Nidhikhare12/OsdagBridge#128](https://github.com/Nidhikhare12/OsdagBridge/issues/128) (open, 2026-11-17) — draft: `notes/issue_drafts/12_example_basic_vacuous_validation.md`
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

## Phase 3 — Validation rule drift (2026-11-17)

### P3-001 — `validate_material_inputs` has no range-validation branches for cross-bracing/end-diaphragm material keys (T2)
- **Tier:** T2 (Likely bug / validation gap)
- **Filed:** [Nidhikhare12/OsdagBridge#129](https://github.com/Nidhikhare12/OsdagBridge/issues/129) (open, 2026-11-17) — draft: `notes/issue_drafts/10_p3_validate_material_inputs_missing_cb_ed_branches.md`
- **Area:** Phase 3 — `core/bridge_types/plate_girder/validator.py` `BridgeInputValidator.validate_material_inputs`
- **Duplicate check:** searched refreshed issues (through #126) via `scripts/search_issues.py`: `cross_bracing.fy`/`end_diaphragm.fy` no direct match; #118 covers cross-field consistency (fu<fy, G vs E,ν) and per-field dialog checks but not missing core per-field branches for CB/ED; #43/#125 cover storage/consumption/staleness, not range validation. **No duplicate found.**
- **Evidence:** `scripts/drift_check.py` + `evidence/logs/phase3_drift_check.txt` (executed in `osdagbridge-env`, clone on sys.path). Calls show girder ranges enforced but cross-bracing/end-diaphragm keys accepted without correction:
  - `validate_material_inputs(KEY_MATERIAL_GIRDER_FY, 5000)` → rejected `(1200.0, 'Yield Strength, Fy must be between 100.0 and 1200.0 MPa.')`
  - `validate_material_inputs(KEY_MATERIAL_CROSS_BRACING_FY, 5000)` → `ACCEPTED (None)`
  - `validate_material_inputs(KEY_MATERIAL_END_DIAPHRAGM_FY, 5000)` → `ACCEPTED (None)`
  - CB/ED samples also accepted: `material.cross_bracing.fu=2000`, `material.cross_bracing.e=500`, `material.cross_bracing.density=200`, `material.end_diaphragm.fu=2000`, `material.end_diaphragm.density=200` → `ACCEPTED`. No stiffener material keys found in `common.py`.
- **Code (read-only):** `validator.py:78-172` implements branches only for `KEY_MATERIAL_GIRDER_*` and `KEY_MATERIAL_DECK_*`; `material.cross_bracing.*` and `material.end_diaphragm.*` keys fall through to `return None`.
- **Expected vs actual:** per-field custom material range validation should apply consistently to all steel components that accept custom properties (girder, cross bracing, end diaphragm) or be explicitly scoped; **actual:** core `validate_material_inputs` validates girder/deck only and silently accepts out-of-range CB/ED material values.
- **Notes:** dialog-level behavior and custom-material flows differ (see #118/#43/#76/#125); this finding is specific to `BridgeInputValidator.validate_material_inputs`. OSI load-time also skips material validation (#96).

### P3-002 — OSI validator does not police unknown enum values for `structure.type`, `geometry.include_median`, `geometry.footpath` (T7)
- **Tier:** T7 (Oddity that might be intended; tolerant load behavior)
- **Area:** Phase 3 — `core/utils/osi_validator.py`
- **Duplicate check:** no matching issue found for these specific enum keys being accepted at OSI load (design.mode is validated; #96 covers material keys).
- **Evidence:** `evidence/logs/phase3_drift_check.txt`: `OsiInputValidator().validate({...})` returns `valid=True, errors=[]` for `structure.type='Railway Bridge'`, `geometry.include_median='Maybe'`, `geometry.footpath='Triple'`. `design.mode` unknown is correctly rejected when using `KEY_DESIGN_MODE` (`geometry.design_mode`): `valid=False` with expected-modes error (separate probe in log/session). OSI validator only runs `_validate_design_mode` and present-value checks for `_BASIC_KEYS`/`_ADDITIONAL_KEYS`.
- **Expected vs actual:** unknown/unsupported enum selections could be rejected at load for consistency; **actual:** accepted (tolerant). May be intentional to avoid blocking hand-edited files, but can defer invalid state to later stages.

### P3-003 — `_ADDITIONAL_KEYS` entries with no numeric bound enforced by `validate_additional_inputs` (T3)
- **Tier:** T3 (Static/executed observation — bounds may be intentionally unspecified)
- **Area:** Phase 3 — `validator.py` vs `osi_validator.py` `_ADDITIONAL_KEYS`
- **Duplicate check:** not searched as a single umbrella issue (heterogeneous keys); no specific duplicate identified.
- **Evidence:** `evidence/logs/phase3_drift_check.txt`: of 57 `_ADDITIONAL_KEYS`, 41 produced a limit response to extreme values (±1e9) and **16 produced no limit response** (accepted/None, no exception): `loading.live_load.footpath_pressure.value`, `loading.seismic_load.dead_load.value`, `loading.seismic_load.live_load.value`, `loading.wind_load.gust_factor.value`, `loading.wind_load.drag_coeff.value`, `loading.wind_load.drag_coeff_ll.value`, `loading.wind_load.lift_coeff.value`, `loading.wind_load.super_area_elev.value`, `loading.wind_load.super_area_plain.value`, `loading.wind_load.exposed_frontal_area.value`, `loading.temperature_load.thermal_coeff_steel`, `loading.temperature_load.thermal_coeff_rcc`, `design_options.shear_studs.height`, `design_options.shear_studs.transverse_spacing`, `design_options_cont.camber.mode`, `design_options_cont.camber.value`. `osi_validator` delegates to `validate_additional_inputs`, so load-time behavior matches (no bounds) for these when present.
- **Notes:** some are mode/non-numeric or may be intentionally unbounded; not asserted as bugs without domain-specific limits. Recorded for drift visibility.

### P3-004 — Basic/median cross-field and basic ranges consistent at core and OSI-load (present values) (T8)
- **Tier:** T8 (Checked and correct, within tested scope)
- **Area:** Phase 3 — `validate_basic_inputs` vs `osi_validator`
- **Evidence:** `evidence/logs/phase3_drift_check.txt`: span/cw/skew basic keys enforced by both (present-only at load). Median Yes with carriageway 6.0 m rejected consistently: `validate_basic_inputs` returns required width 7.50 m; `osi_validator` returns `valid=False` with same error. Material girder/deck ranges enforced in `validate_material_inputs`; OSI load still skips `material.*` keys (consistent with #96).

### P3-005 — Lint (ruff/pyflakes) on `src/osdagbridge/core` unavailable in environment (T9)
- **Tier:** T9 (Could not test as requested tool unavailable)
- **Area:** Phase 3 — static lint
- **Evidence:** `evidence/logs/phase3_lint_core.txt` shows `ruff`, `pyflakes`, and `flake8` not found (env/system).
- **What blocked:** no requested linter installed; top-10 triage not produced.

## Tracks F–I (validation fuzz, location/weather, LaTeX escaping, OSI file I/O) — 2026-11-17 (session 2)

### P4F-001 — Integer additional-input validators raise `OverflowError` on `inf`/`-inf` instead of a validation message (T2)
- **Tier:** T2 (Likely bug — uncaught exception)
- **Filed:** [Nidhikhare12/OsdagBridge#130](https://github.com/Nidhikhare12/OsdagBridge/issues/130) (open, 2026-11-17) — draft: `notes/issue_drafts/14_validator_integer_fields_raise_overflowerror_on_inf.md`
- **Area:** Track F — `core/bridge_types/plate_girder/validator.py` `validate_additional_inputs` / `_to_int`
- **Duplicate check:** `scripts/search_issues.py "OverflowError"`, `"infinity"` on refreshed `notes/issues_raw.json` — no match. #88 is NaN/nonfinite acceptance (different symptom).
- **Evidence (executed):** `scripts/validator_fuzz.py` → `evidence/logs/trackF_validator_fuzz.txt`, `evidence/logs/trackF_validator_fuzz.json` (5460 calls, 242 flags, 10 exceptions). `inf`/`-inf` cause `OverflowError: cannot convert float infinity to integer` for `KEY_TS_NO_OF_GIRDERS`, `KEY_WC_LD_LANE_TABLE_COUNT`, `KEY_MP_CB_NO_OF_CROSS_BRACINGS`, `KEY_DS_STUD_COUNT`, `KEY_DO_LOAD_CYCLES` (2 values × 5 keys).
- **Expected vs actual:** invalid non-finite integer input should yield a validation correction/message; **actual:** uncaught `OverflowError`.
- **Draft:** `notes/issue_drafts/14_validator_integer_fields_raise_overflowerror_on_inf.md`

### P4F-002 — Non-finite `NaN`/`inf` accepted as valid by many validators (T4, dup/root-cause overlap #88)
- **Tier:** T4 (Duplicate root-cause overlap — #88 NaN/nonfinite acceptance)
- **Area:** Track F — `validate_basic_inputs`, `validate_material_inputs`, `validate_additional_inputs` (via `_to_float`/comparison behavior)
- **Duplicate check:** #88 "[Bug] OSI validation accepts NaN physical inputs..." cites `BridgeInputValidator._to_float` and nonfinite handling; same underlying acceptance of NaN/nonfinite values.
- **Evidence (executed):** `scripts/validator_fuzz.py` flags `naninf_valid` = 132 (basic 3, material 12, additional 117) where validators returned `None` (treated as valid) for `nan` (and in some cases related non-finite paths). Log: `evidence/logs/trackF_validator_fuzz.txt/json`.
- **Extra detail:** scope extends across many material/additional keys beyond examples in #88; `inf` on float-handled paths can be accepted or trigger other behavior depending on branch (separate from integer OverflowError in P4F-001).

### P4F-003 — `bool` values accepted as numeric inputs in multiple validators (T7)
- **Tier:** T7 (Oddity; Python `bool` is `int` subclass — sometimes numerically within range)
- **Area:** Track F — numeric validators
- **Duplicate check:** no specific existing issue found for bool-as-number acceptance.
- **Evidence (executed):** `scripts/validator_fuzz.py` flags `bool_valid` = 100 (e.g. `geometry.skew_angle` accepts `True/False`, various material/additional keys accept `True/False` when coerced value falls in range). Full list in `evidence/logs/trackF_validator_fuzz.json`.
- **Notes:** not all are invalid (e.g. False==0 can be in-range), but accepting booleans as numeric inputs may be unintended; recorded as executed oddity.

### P4G-001 — Map coordinate validator accepts out-of-range and out-of-India coordinates; weather validator accepts unknown zone strings (T7)
- **Tier:** T7 (Oddity/weak validation; behavior may be intentional scope)
- **Area:** Track G — `validate_map_coordinates`, `validate_custom_weather_data`
- **Duplicate check:** no matching existing issue found for these specific cases.
- **Evidence (executed):** `scripts/location_fuzz.py` → `evidence/logs/trackG_location_weather.txt/json` (34 cases, 0 exceptions). `validate_map_coordinates` returns valid for out-of-range lat/lon (90.0001, 180.0001), swapped lat/lon, and outside-India location (40.7128,-74.0060); only checks non-empty numeric parse. `validate_custom_weather_data` rejects `Select Zone` but accepts `UNKNOWN` and empty string as zone when wind/temps valid.
- **Notes:** module is IRC/India-context per task; validator does not enforce geographic/zone bounds beyond current checks.

### P4H-001 — LaTeX escaping for free-text report fields not fully verified headlessly (T3)
- **Tier:** T3 (Static/partial — not fully executed end-to-end)
- **Area:** Track H — `core/reports/*`
- **Duplicate check:** many report/LaTeX issues exist; did not claim new bug without executed failing repro.
- **Evidence (read-only):** `grep` found no `pylatex/NoEscape/escape_latex`; custom escaping present in `core/reports/report_utils.py` (e.g. backslash/colon handling) and partial char escaping in `core/reports/chap8.py` (`_ % & #`). `report_generator.py` invokes pdflatex via `osdag_latex_env`/subprocess (per grep). No headless report generation with special-char strings (`A&B`, `%`, `_`, `#`, `{}`, `$`, `~`, `^`, unicode, 300-char) executed this session.
- **What blocked:** end-to-end report build with controlled free-text inputs not exercised; completeness of escaping for all user free-text fields (project name/client/location/remarks etc.) remains unverified.

### P4I-001 — `saveOSI_inputs` uses `yaml.dump` (unsafe tags) incompatible with `yaml.safe_load` on load (T2)
- **Tier:** T2 (Likely save/load round-trip bug)
- **Filed:** [Nidhikhare12/OsdagBridge#131](https://github.com/Nidhikhare12/OsdagBridge/issues/131) (open, 2026-11-17) — draft: `notes/issue_drafts/15_save_osi_yaml_dump_unsafe_tags_break_safe_load.md`
- **Area:** Track I — `desktop/ui/template_page.py` save/load OSI
- **Duplicate check:** `scripts/search_issues.py "yaml.dump"`, `"python/object"`, `"safe_load"` — no matching issue for unsafe-dump vs safe-load incompatibility.
- **Evidence (executed):** `evidence/logs/trackI_yaml_dump_safe_load.txt`: `yaml.dump({"a": np.float64(1.5), "t": (1,2), "s": {1,2}})` emits `!!python/...`, `!!python/tuple`, `!!set`; `yaml.safe_load` raises `ConstructorError`. Code: `saveOSI_inputs` (~793–820) calls `yaml.dump(self.input_dict, input_file)`; `loadOSI_inputs` (~827+) calls `yaml.safe_load(f)`.
- **Expected vs actual:** saved OSI should round-trip via safe load; **actual:** unsafe tags can make saved files unloadable.
- **Draft:** `notes/issue_drafts/15_save_osi_yaml_dump_unsafe_tags_break_safe_load.md`

### P4I-002 — OSI save/load static observations (extension handling, overwrite, error paths) (T8/T7 mix, partial)
- **Tier:** T8/T7 (checked behavior/observations, static + limited reasoning)
- **Area:** Track I — `desktop/ui/template_page.py` save/load
- **Evidence (read-only):** `saveOSI_inputs` does not append `.osi` if missing or normalize case (`.OSI`/`.yaml`) — relies on dialog/filter; overwrite confirmation not explicitly coded (OS/dialog-dependent). `loadOSI_inputs` catches exceptions and shows error (no "Loaded OSI Successfully!" on failure), rejects non-dict/invalid via `validate_osi_inputs` before populate, but `populate_from_dict` called after validation (partial-state risk if populate throws mid-way is implementation-dependent). Empty/binary/dir/permission errors surface via exception handler.
- **Notes:** no GUI-driven file I/O execution this session (T3 for unexecuted paths); yaml round-trip type issue captured separately as P4I-001.

### P5-006 — Wrong PASS: silent live-load skip → zero ULS demand (median Yes + Both Sides footpath + cw 7.5) (T1)
- **Tier:** T1 (Confirmed wrong PASS — executed and reproduced)
- **Filed:** [Nidhikhare12/OsdagBridge#134](https://github.com/Nidhikhare12/OsdagBridge/issues/134) (open, 2026-11-17) — draft: `notes/issue_drafts/18_zero_live_load_wrong_pass_median_both_footpaths.md`
- **Area:** Phase 4 — crash/timeout sweep (SW05) + targeted repro
- **Duplicate check:** searched `governing LL`, `live-load`, `zero` DCR — #87 (seismic zero-LL mass) and #45 (missing DCR shown 0.0) related but different triggers; no exact duplicate.
- **Evidence (executed):** SW05 / P5_SW05R (span30, cw7.5, skew0, footpath Both Sides, median Yes) → `analyser.py:1998` warning "Envelope-based governing LL detection failed ('Element' index)... skipping LL creation" + 26 live-load warnings; `mu_applied=0.0`, all `util.*=0.0`, ULS Flexure/Shear DCR 0.000, verdict **PASS** (max DCR 0.2853 from a stiffener check excluded from structural set). Four controls with one field changed (no median / no footpath / cw10.5) show 0 warnings and normal demands (flexure 22–30%, fatigue 186–242%). Reproduced twice (SW05, P5_SW05R).
- **Root cause:** `analyser.py:1991` `env_lc.sel(Element=gov_element)` KeyError swallowed by broad `except` (:1998) → `ll_load_case=None` → no ULS LL → zero demand → PASS.
- **Expected vs actual:** nonzero live-load demand expected; **actual:** zero demand + PASS (unconservative).

### P5-005 — `design()` non-termination on valid span-45 + median + footpath inputs (T2)
- **Tier:** T2 (likely performance/hang bug)
- **Filed:** [Nidhikhare12/OsdagBridge#133](https://github.com/Nidhikhare12/OsdagBridge/issues/133) (open, 2026-11-17) — draft: `notes/issue_drafts/17_design_nontermination_span45_median_footpath.md`
- **Area:** Phase 4 — crash/timeout sweep
- **Duplicate check:** searched `hang`/`slow`/`timeout`/`non-converg` in refreshed issues — no match. No duplicate.
- **Evidence (executed):** SW03 (span45, cw15, skew−15, foot Both Sides, median Yes) and SW06 (span45, cw15, skew+15, foot Single Side, median Yes) both exceeded the 600 s per-case timeout (`evidence/logs/design_sweep_run.log`); SW03 rerun without timeout consumed >12 min CPU with no result before being stopped. Controls complete in 28–261 s. `fsolve` non-convergence warning (`ospgrillage/utils.py:555`) and repeated `thermal_load not available` warnings in case logs.
- **Expected vs actual:** valid in-limits inputs should finish in time comparable to other cases or raise a clear error; **actual:** hangs >10 min with no output.

## Phase 4 — headless design harness + oracle/metamorphic (2026-11-17, session 3)

### P5-004 — Skew sign is not mirror-symmetric: +θ vs −θ give different design demands (T2)
- **Tier:** T2 (likely analysis bug — sign-dependent results)
- **Filed:** [Nidhikhare12/OsdagBridge#132](https://github.com/Nidhikhare12/OsdagBridge/issues/132) (open, 2026-11-17) — draft: `notes/issue_drafts/16_skew_sign_mirror_asymmetry.md`
- **Area:** Phase 4 — mirror-symmetry metamorphic check (analysis)
- **Duplicate check:** `scripts/search_issues.py` for `skew`/`mirror`/`asymmetric`: closest #89 (skewed per-girder omission), #124 (inconsistent width) — neither compares +θ vs −θ sign. No duplicate.
- **Evidence (executed):** headless designs from defaults, span 30 / cw 10.5 / no median / no footpath / Optimized, only skew sign differs. ±15°: `util.shear` 59.28 vs 41.08, `util.fatigue` 183.74 vs 167.06, `util.mu_applied` 2602.12 vs 2376.38; ±7.5°: `util.shear` 62.32 vs 42.18, `util.fatigue` 182.25 vs 175.33. Self-weight checks identical (`util.long_trans_shear` 21.52 both; stiffener leg 1.479 both). Confirmed in two independent sign pairs (`dictionaries/OR_SKEW*/output.json`, `evidence/logs/oracle_runs1.log`, `oracle_runs2.log`).
- **Expected vs actual:** for a symmetric section, +θ and −θ are mirror images → equal demand magnitudes; **actual:** +skew consistently ~44–48% higher shear, ~9% higher moment. Sign of symmetric parameter affects design.
- **Likely area:** `analyser.py` `create_grillage(skew=self.angle, mesh_type="Oblique")` (~L275) + `load_placement.py` load mapping; exact line under investigation.

### P5-001 — Headless design harness works from defaults (no baseline.osi required) (T8)
- **Tier:** T8 (checked and correct — harness capability)
- **Area:** Phase 4 — `scripts/design_runner.py`
- **Evidence (executed):** built a 688-key input dict from `BASIC_INPUT_DICT` + `solve_extend_basic_input_dict` + `prime_material_inputs(in_session)`; `PlateGirderBridge().set_input(d); design()` completed (`dictionaries/SMOKE/result.json`: status ok, runtime 71.7–79.1 s, 1304 top-level output keys). `project.location=None` is handled by design (seismic falls back to Zone II z=0.10) — no weather data invented.
- **Notes:** `design()` returns `output_dict` as a `mappingproxy`; harness converts via `dict()`. 25-case crash sweep launched (`scripts/design_sweep.py`, `evidence/logs/design_sweep_run.log`).

### P5-002 — Smoke-case output invariants pass (T8)
- **Tier:** T8 (checked and correct)
- **Area:** Phase 4 — invariant/oracle check on `dictionaries/SMOKE/output.json`
- **Evidence (executed):** 0 NaN/inf values, 0 negative thickness/depth/width among scalar output fields; `util.*` values 21.52–187.06 (these are DCR×100 percent, confirmed by `plategirderbridge.py:4102` `*100` and `report_generator` `/100` in `chap5.py:219`); `steeldesign.details.moment.mu_applied=2646.84` kNm vs `md_capacity=11477.22` kNm → DCR 0.231, consistent with printed design-check table. Units consistent across keys (section depth 1.67 m in `member_properties` vs 1670 mm in `steeldesign.details.total_depth`).

### P5-003 — "thermal_load load case not available" warnings at load combinations (T4, dup #92)
- **Tier:** T4 (Duplicate — #92 "canonical temperature inputs do not create thermal load cases")
- **Area:** Phase 4 — smoke-case log
- **Evidence (executed):** `evidence/logs/design_smoke2.log` shows repeated `UserWarning: BASIC_1..BASIC_6, ACCIDENTAL_1: 'thermal_load' load case not available — create it before calling create_uls_combinations()` (analyser.py:2381). Same root condition as #92; not re-reported.

### P5-006b — Wrong-PASS #134 trigger is broader than filed (extra evidence for comment) (T1)
- **Tier:** T1 (extra reproduction of confirmed wrong PASS)
- **Relates to:** #134 (already filed) — comment draft `notes/issue_drafts/18b_comment_issue134_more_wrong_pass_triggers.md`, posting pending
- **Evidence (executed):** SW15 (span45, cw23.6, skew−7.5, footpath None, median No) → same `analyser.py:1998` "Envelope-based governing LL detection failed ('Element' index)" warning, `mu_applied=0.0`, all util 0, verdict PASS (max DCR 0.4545 from excluded checks). Different span/width/skew/median/footpath than #134's trigger → the bug is in the governing-LL envelope element lookup itself, not a specific geometry. Not solely girder count (SW07/09/13/14/21 with 10–11 girders complete normally).
- **Action:** comment draft prepared for #134; do not file as new issue (duplicate of #134).

### P5-007 — Idempotence crash: second `design()` on same object fails in LTB buckling (T1)
- **Tier:** T1 (Confirmed crash — executed)
- **Filed:** [Nidhikhare12/OsdagBridge#135](https://github.com/Nidhikhare12/OsdagBridge/issues/135) (open, 2026-11-17) — draft: `notes/issue_drafts/19_idempotence_second_design_crash.md`
- **Duplicate check:** `second run`/`math domain`/`Mcr`/`redesign` — #85 closest (CAD display on 2nd run, no design-error dialog), different failure; no duplicate.
- **Evidence (executed):** guarded harness (with `__main__`), `dictionaries/IDEM2/same.py`: call #1 `RUN1_DONE` (normal), call #2 → `ValueError: math domain error` at `irc22_2015.py:639` `math.sqrt(beta_b*(Zp*fy)/Mcr)`, via `designer.py:1007 compute_buckling_resistance`, stage 5 `_run_dcr_checks` (`evidence/logs/determinism_2.log`, full traceback `dictionaries/IDEM2/same.log`). Earlier unguarded `IDEM` run was a forkserver re-exec artifact and discarded.
- **Input:** default span30/cw10.5/skew0/no median/no footpath/Optimized (the normal SW01 case) — valid.
- **Expected vs actual:** two consecutive `design()` calls on one object should not crash; **actual:** 2nd call crashes in LTB check.

### P5-008 — Sweep completion summary (25 cases) (T8/T1/T2 mix)
- **Tier:** record of outcomes (not a single finding)
- **Evidence:** `test_cases/sweep_results.csv` (25 rows), `evidence/logs/design_sweep_run.log`, `evidence/logs/design_sweep_resume.log`.
- **25 cases:** 3 timeouts (SW03/SW06 span45+median+footpaths → #133; SW23 also timeout 600 s), 3 wrong-PASS zero-demand (SW05, SW15, SW22 → #134), 19 completed with finite outputs; no crashes/exceptions on completed cases; no wrong PASS/FAIL verdicts among checked DCR rows. SW23 (span 35, cw 23.6, skew 7.5, footpath Both Sides, median Yes) timed out — same non-termination class as #133; add to that issue as extra evidence.)

### P5-009 — Custom material Fy and Optimized→Custom round-trip checks (T8; two false positives avoided)
- **Tier:** T8 (Checked and correct) + record of discarded artifacts
- **Evidence (executed):**
  - Custom girder Fy 380 vs 450 (built from defaults, material.girder=custom): flexure util 21.44 → 18.42 (changes as expected); shear/fatigue unchanged (not yield-governed). Custom Fy is consumed — PASS.
  - Optimized→Custom round-trip: feeding Optimized's exact chosen dims (depth 1670 mm, web 1628, flanges 510×22, web tw 10) into a properly-built Custom dict (`RT_Custom3`) gives flex 23.26 / fatigue 188.74 vs Optimized 23.06 / 187.06, moment 2669 vs 2647 kNm — within ~1% (SAIL thickness snapping explains residual). PASS.
  - **Discarded false positives:** (a) hand-built `RT_Custom` with fabricated G6/G7 dims gave `total_depth=1,670,000` mm and absurd DCRs — caused by my inconsistent input, not a product bug; (b) unguarded determinism harness `IDEM` forkserver re-exec artifact — discarded. Report relies only on properly-built/gaurded runs.
- **No new issue filed** from these checks.

### P5-010 — Hand statics check: reported DL moment/reaction plausible from first principles (T8)
- **Tier:** T8 (Checked and correct, within justified tolerance)
- **Area:** Phase 4 — oracle hand-check on SMOKE (span30, cw10.5, 5 girders, Optimized)
- **Evidence (executed + hand calc):** from `dictionaries/SMOKE/output.json`: girder mass 274.1124 kg/m → 2.689 kN/m self-weight; deck 0.25 m × 24.5 kN/m³ × 2.28 m tributary = 13.965 kN/m; total w ≈ 16.65 kN/m per girder. Simple statics `wL²/8` (L=30 m) → M_DL ≈ 1874 kNm. Reported ULS `mu_applied = 2646.84` kNm → ratio 1.41. DL reaction `wL/2` ≈ 250 kN/girder; reported bearing reaction 472.49 kN → ratio 1.89. Log: total DL 2981.4 kN (5 girders → ~596 kN each over 30 m ≈ 19.9 kN/m) consistent with hand w + wearing course/crash barriers.
- **Expectation & tolerance:** `mu_applied` is a factored ULS combination (dead + live + partial factors γ≈1.35–1.5 + impact), so it must exceed the unfactored DL-only moment by a factor of order 1.3–2.0; observed 1.41 (moment) and 1.89 (reaction) fall in that band. Exact load factors/distribution are not applied here (not guessed per rules), so this is a plausibility check, not an exact recomputation.
- **Conclusion:** no inconsistency found; results are in plausible relation to inputs. Not a bug.
