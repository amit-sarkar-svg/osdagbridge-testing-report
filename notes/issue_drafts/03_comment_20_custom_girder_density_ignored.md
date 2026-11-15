# Comment draft — #20: Custom steel density from UI/input_dict is ignored in `_build_material_props`

**Target:** https://github.com/Nidhikhare12/OsdagBridge/issues/20 (duplicate/extra detail; not a new issue)  
**Audit ref:** P2-003 (T4) — OsdagBridge `dev @ d74f56d`, testing repo `osdagbridge-testing-report`

## Suggested comment (copy/paste)

Extra detail (static audit, read-only on `dev @ d74f56d`) confirming the custom-girder-density gap and showing the UI/validation/report side also references the key:

**Design build path ignores custom density on DB-miss**  
`src/osdagbridge/core/bridge_types/plate_girder/plategirderbridge.py:1175-1215` (`_build_material_props`): for a custom grade (DB lookup returns `None`) it reads `E, v (poisson), Fy, Fu` from `KEY_MATERIAL_GIRDER_*` subkeys, but **density** is handled as:
```python
rho = self._lookup_material(steel_grade, "Density")
if rho is None:
    rho = _DEFAULT_DENSITY  # 78500.0 N/m³ — never reads KEY_MATERIAL_GIRDER_DENSITY
```
So `material.girder.density` / `KEY_MATERIAL_GIRDER_DENSITY` is never used as the custom fallback in the design material build.

**Key is present in UI/validator/report**
- UI/custom dialog + priming write girder material subkeys (including density) into `input_dict` (`dialogs/material_properties.py` export/priming path; `docks/input_dock.py` priming/apply).
- Core references (per `notes/ui_key_map.csv`): `core/bridge_types/plate_girder/validator.py`, `core/reports/chap3.py`, `core/utils/common.py` (in addition to the missing design-consumption in `_build_material_props`).

**Duplicate check:** aligns with #20; adding the exact fallback logic and the validator/report references for triage.
