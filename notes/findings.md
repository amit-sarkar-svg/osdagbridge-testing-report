# Findings (candidate bugs)

Status: WIP. Nothing here is final until it reproduces on a second fresh run
and the duplicate check against notes/existing_issues.md (39 issues, fetched
2026-11-15) is recorded.

## F1 — Validator accepts NaN span (and any NaN physical input it compares)
- Severity: high
- Duplicate check: DUPLICATE of **#88** ("OSI validation accepts NaN physical
  inputs before layout and model construction") — extra root-cause detail to
  comment on #88, not a new issue.
- Reproduction (confirmed by pytest, run 2026-11-15):
  `BridgeInputValidator().validate_basic_inputs("geometry.span", {"geometry.span": float("nan")})`
  returns `None` (= valid). Reproduced twice (two pytest invocations).
- Expected: NaN rejected ("Span must be a numeric value").
- Actual: accepted; NaN then flows into layout solving.
- Evidence: `tests/test_validator_limits.py::test_nan_span_behaviour` (failing
  test, intentional), pytest output in notes/run_history.md.
- Root cause: `_to_float` (validator.py L1094–1098) returns `float(nan)`
  unchecked; boundary checks `span < SPAN_MIN` / `span > SPAN_MAX`
  (validator.py L32–35) are both False for NaN, so no error is raised.
- Suggested fix:
  ```diff
  --- validator.py
  @@ def _to_float(self, value):
       try:
  -        return float(value)
  +        v = float(value)
  +        return v if math.isfinite(v) else None
       except (TypeError, ValueError):
           return None
  ```

## F2 — Custom steel density is never read by the design pipeline (from code study)
- From source reading only: `_build_material_props` (plategirderbridge.py
  L1169–1215) reads custom E/Fy/Fu/Poisson from material.girder.* but takes
  density from the DB or `_DEFAULT_DENSITY = 78500 N/m³` (L1177), never from
  `material.girder.density`.
- DUPLICATE of **#20** ("Custom steel density from UI/input_dict is ignored in
  _build_material_props"). To be CONFIRMED at runtime with SN04 vs SN01
  sensitivity check (self-weight identical despite density 77→50).

## F3 — OSI load does not validate material.* keys (CONFIRMED 2026-11-15)
- **FILED as issue #96** — https://github.com/Nidhikhare12/OsdagBridge/issues/96
  (was NEW: not covered by any of the 39 existing issues; checked bodies of
  #19, #20, #41, #76, #84, #88 — all different).
- Runtime proof: `validate_osi_inputs({fy: 99999, density: 5, fck: -3})`
  → `is_valid = True`, zero errors; the same values ARE rejected by
  `validate_material_inputs`. Evidence: `evidence/analyze/osi_material_bypass.txt`.
- Root cause: osi_validator.py `_BASIC_KEYS` (L82–86) + `_ADDITIONAL_KEYS`
  (L89–111) contain no `material.*` keys, so `validate_material_inputs` is
  unreachable from the load path (template_page.py `loadOSI_inputs` L847).
  The live material dialog enforces the same limits, so only hand-edited
  .osi files bypass them.
- Suggested fix:
  ```diff
  --- osi_validator.py
  @@ _ADDITIONAL_KEYS = [
  +    # custom material limits - same rules the Material dialog enforces live
  +    KEY_MATERIAL_GIRDER_DENSITY, KEY_MATERIAL_GIRDER_FY, KEY_MATERIAL_GIRDER_FU,
  +    KEY_MATERIAL_GIRDER_E, KEY_MATERIAL_GIRDER_G, KEY_MATERIAL_GIRDER_POISSON,
  +    KEY_MATERIAL_GIRDER_THERMAL,
  +    KEY_MATERIAL_DECK_DENSITY, KEY_MATERIAL_DECK_FCK, KEY_MATERIAL_DECK_FCTM,
  +    KEY_MATERIAL_DECK_ECM, KEY_MATERIAL_DECK_THERMAL,
       ...
  ]
  ```
  (validate() must then call `validate_material_inputs` for these keys in
  addition to `validate_additional_inputs`.)

## F4 — Custom-grade material values wiped at Design after OSI load (from code study + live emulation)
- input_dock._prime_material_inputs (L324–342) runs before every Design
  (template_page.py L636). After an OSI load, `_material_custom_fields` is
  empty (issue #19), so the dialog for a custom grade produces empty fields
  and `_update_input_dict` (input_dock.py L1029–1046) overwrites the loaded
  values with None. Verified live via ui_emulation.py on 2026-11-15:
  `material.girder.fy: '355.0' -> None` for grade "QA_CustomSteel".
- DUPLICATE of **#19** (already filed). Runtime confirmation pending via CM01
  (osi_load mode vs in_session mode outputs).
