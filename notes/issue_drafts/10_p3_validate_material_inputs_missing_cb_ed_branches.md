# [Bug/Validation] `validate_material_inputs` skips range checks for cross-bracing/end-diaphragm material keys

**Filed:** [Nidhikhare12/OsdagBridge#129](https://github.com/Nidhikhare12/OsdagBridge/issues/129) — open (filed 2026-11-17)

**Environment**
- OsdagBridge `dev` @ `d74f56d` (2026-07-26)
- macOS (Intel), conda env `osdagbridge-env`, Python 3.12.16
- Executed via direct validator calls (no design run, no `baseline.osi`)
- Finding type: **T2 (likely validation bug/gap)**

**Description**
`BridgeInputValidator.validate_material_inputs` enforces per-field numeric ranges for girder and deck custom material properties, but it has no validation branches for cross-bracing or end-diaphragm material keys. As a result, out-of-range values for `material.cross_bracing.*` and `material.end_diaphragm.*` are accepted (function returns `None`) instead of being corrected/rejected like equivalent girder/deck fields.

**Steps / Reproduction (executed)**
From a Python session with `OsdagBridge/src` on `sys.path`:
```python
from osdagbridge.core.bridge_types.plate_girder.validator import BridgeInputValidator
from osdagbridge.core.utils.common import (
    KEY_MATERIAL_GIRDER_FY,
    KEY_MATERIAL_CROSS_BRACING_FY, KEY_MATERIAL_CROSS_BRACING_FU,
    KEY_MATERIAL_CROSS_BRACING_E, KEY_MATERIAL_CROSS_BRACING_DENSITY,
    KEY_MATERIAL_END_DIAPHRAGM_FY, KEY_MATERIAL_END_DIAPHRAGM_FU,
    KEY_MATERIAL_END_DIAPHRAGM_DENSITY,
)

bv = BridgeInputValidator()

# girder (range enforced)
print(bv.validate_material_inputs(KEY_MATERIAL_GIRDER_FY, {KEY_MATERIAL_GIRDER_FY: 5000}))
# -> (1200.0, 'Yield Strength, Fy must be between 100.0 and 1200.0 MPa.')

# cross-bracing / end-diaphragm (no branch -> accepted)
print(bv.validate_material_inputs(KEY_MATERIAL_CROSS_BRACING_FY, {KEY_MATERIAL_CROSS_BRACING_FY: 5000}))
print(bv.validate_material_inputs(KEY_MATERIAL_END_DIAPHRAGM_FY, {KEY_MATERIAL_END_DIAPHRAGM_FY: 5000}))
print(bv.validate_material_inputs(KEY_MATERIAL_CROSS_BRACING_FU, {KEY_MATERIAL_CROSS_BRACING_FU: 2000}))
print(bv.validate_material_inputs(KEY_MATERIAL_CROSS_BRACING_E, {KEY_MATERIAL_CROSS_BRACING_E: 500}))
print(bv.validate_material_inputs(KEY_MATERIAL_CROSS_BRACING_DENSITY, {KEY_MATERIAL_CROSS_BRACING_DENSITY: 200}))
print(bv.validate_material_inputs(KEY_MATERIAL_END_DIAPHRAGM_FU, {KEY_MATERIAL_END_DIAPHRAGM_FU: 2000}))
print(bv.validate_material_inputs(KEY_MATERIAL_END_DIAPHRAGM_DENSITY, {KEY_MATERIAL_END_DIAPHRAGM_DENSITY: 200}))
# -> None for each (accepted)
```

**Expected behavior**
Custom material per-field range validation should apply consistently to steel components that accept custom material properties (girder, cross bracing, end diaphragm), or the validator should clearly scope/handle unsupported component keys so out-of-range CB/ED values are not silently accepted.

**Actual behavior**
`validate_material_inputs` validates `KEY_MATERIAL_GIRDER_*` and `KEY_MATERIAL_DECK_*` only; `material.cross_bracing.*` and `material.end_diaphragm.*` keys (and no stiffener material keys are defined in `common.py`) fall through to `return None`, so out-of-range values are accepted.

**Logs / proof**
- `scripts/drift_check.py`
- `evidence/logs/phase3_drift_check.txt` (executed output showing girder rejected, CB/ED accepted for extreme values)

**Root cause (file:line, read-only)**
`src/osdagbridge/core/bridge_types/plate_girder/validator.py` — `BridgeInputValidator.validate_material_inputs` (≈L78–L172) contains conditional branches only for girder and deck material keys:
```py
# ── Weight Density (kN/m³) ──────────────────────────────────────────────
if key == KEY_MATERIAL_GIRDER_DENSITY:
    ...
# ── Yield Strength, Fy (MPa) ────────────────────────────────────────────
elif key == KEY_MATERIAL_GIRDER_FY:
    ...
...
# ── Deck: ... ──
elif key == KEY_MATERIAL_DECK_THERMAL:
    ...
return None
```
No corresponding branches exist for `KEY_MATERIAL_CROSS_BRACING_*` or `KEY_MATERIAL_END_DIAPHRAGM_*` (defined in `core/utils/common.py`, e.g. L76–L90), so those keys are not range-checked.

**Suggested fix (diff idea)**
Add per-field validation for cross-bracing and end-diaphragm material keys using the same steel ranges as girder (or component-appropriate ranges if specified), e.g. by handling CB/ED Fy/Fu/E/G/Poisson/Thermal/Density alongside girder branches (or via shared helper). Example sketch:
```diff
diff --git a/src/osdagbridge/core/bridge_types/plate_girder/validator.py b/src/osdagbridge/core/bridge_types/plate_girder/validator.py
--- a/src/osdagbridge/core/bridge_types/plate_girder/validator.py
+++ b/src/osdagbridge/core/bridge_types/plate_girder/validator.py
@@
-        # ── Yield Strength, Fy (MPa) ────────────────────────────────────────────
-        elif key == KEY_MATERIAL_GIRDER_FY:
+        # ── Yield Strength, Fy (MPa) — steel members ────────────────────────────
+        elif key in (KEY_MATERIAL_GIRDER_FY, KEY_MATERIAL_CROSS_BRACING_FY, KEY_MATERIAL_END_DIAPHRAGM_FY):
             v = self._to_float(inputs.get(key))
@@
-        elif key == KEY_MATERIAL_GIRDER_FU:
+        elif key in (KEY_MATERIAL_GIRDER_FU, KEY_MATERIAL_CROSS_BRACING_FU, KEY_MATERIAL_END_DIAPHRAGM_FU):
@@
-        elif key == KEY_MATERIAL_GIRDER_E:
+        elif key in (KEY_MATERIAL_GIRDER_E, KEY_MATERIAL_CROSS_BRACING_E, KEY_MATERIAL_END_DIAPHRAGM_E):
@@
-        elif key == KEY_MATERIAL_GIRDER_G:
+        elif key in (KEY_MATERIAL_GIRDER_G, KEY_MATERIAL_CROSS_BRACING_G, KEY_MATERIAL_END_DIAPHRAGM_G):
@@
-        elif key == KEY_MATERIAL_GIRDER_POISSON:
+        elif key in (KEY_MATERIAL_GIRDER_POISSON, KEY_MATERIAL_CROSS_BRACING_POISSON, KEY_MATERIAL_END_DIAPHRAGM_POISSON):
@@
-        elif key == KEY_MATERIAL_GIRDER_THERMAL:
+        elif key in (KEY_MATERIAL_GIRDER_THERMAL, KEY_MATERIAL_CROSS_BRACING_THERMAL, KEY_MATERIAL_END_DIAPHRAGM_THERMAL):
@@
-        if key == KEY_MATERIAL_GIRDER_DENSITY:
+        if key in (KEY_MATERIAL_GIRDER_DENSITY, KEY_MATERIAL_CROSS_BRACING_DENSITY, KEY_MATERIAL_END_DIAPHRAGM_DENSITY):
```
(Confirm intended limits per component/spec before applying; adjust messages to be component-aware if desired.)

**Duplicate check**
Searched refreshed issues (open+closed, PRs skipped, `notes/issues_raw.json` through #126) via `scripts/search_issues.py`: `cross_bracing.fy` / `end_diaphragm.fy` — no direct matches; #118 (cross-field consistency fu<fy, G vs E,ν) different scope; #43/#125 (storage/consumption/staleness of CB/ED custom materials) different scope; #96 (OSI load skips material validation) related but different path. **No duplicate found.**

**Notes**
- Related behavior areas (not claimed as this bug): dialog per-field checks/cross-field consistency (#118, #76), CB/ED custom grade consumption (#43), stale custom material state (#125), OSI load-time material validation gap (#96).
