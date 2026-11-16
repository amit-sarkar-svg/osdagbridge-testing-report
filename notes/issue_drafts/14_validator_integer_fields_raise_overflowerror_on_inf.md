# [Bug/Validation] Integer validators raise `OverflowError` on `inf`/`-inf` instead of returning a validation message

**Filed:** [Nidhikhare12/OsdagBridge#130](https://github.com/Nidhikhare12/OsdagBridge/issues/130) — open (filed 2026-11-17)

**Environment**
- OsdagBridge `dev` @ `d74f56d` (2026-07-26)
- macOS (Intel), conda env `osdagbridge-env`, Python 3.12.16
- Executed via direct validator calls (no GUI, no design run)
- Finding type: **T2 (likely bug — exception instead of handled validation error)**

**Description**
For several integer-valued additional-input keys, `BridgeInputValidator.validate_additional_inputs` raises `OverflowError: cannot convert float infinity to integer` when given `float('inf')` or `float('-inf')`, instead of returning a corrected value/message like other invalid inputs.

**Steps / Reproduction (executed)**
```python
import sys; sys.path.insert(0, "OsdagBridge/src")
from osdagbridge.core.bridge_types.plate_girder.validator import BridgeInputValidator
from osdagbridge.core.utils import common as C

bv = BridgeInputValidator()
for key in [
    C.KEY_TS_NO_OF_GIRDERS,
    C.KEY_WC_LD_LANE_TABLE_COUNT,
    C.KEY_MP_CB_NO_OF_CROSS_BRACINGS,
    C.KEY_DS_STUD_COUNT,
    C.KEY_DO_LOAD_CYCLES,
]:
    for v in (float("inf"), float("-inf")):
        try:
            print(key, v, bv.validate_additional_inputs(key, {key: v}))
        except Exception as e:
            print(key, v, type(e).__name__, e)
```

**Observed (executed)**
- `typical_section.no_of_girders` inf/-inf → `OverflowError: cannot convert float infinity to integer`
- `typical_section.lane_details.lane_table_count` inf/-inf → `OverflowError`
- `member_properties.cross_bracing_details.no_of_cross_bracings` inf/-inf → `OverflowError`
- `design_options.shear_studs.count` inf/-inf → `OverflowError`
- `design_options_cont.fatigue.load_cycles` inf/-inf → `OverflowError`

(10 exception cases total; `scripts/validator_fuzz.py`, `evidence/logs/trackF_validator_fuzz.txt`, `evidence/logs/trackF_validator_fuzz.json`)

**Expected behavior**
Non-finite or otherwise invalid numeric inputs should be handled gracefully and produce a validation correction/message (or a controlled error), not an uncaught exception.

**Actual behavior**
`inf`/`-inf` for these integer fields triggers `OverflowError` during int conversion inside validation.

**Root cause (likely, file:line)**
`src/osdagbridge/core/bridge_types/plate_girder/validator.py` — integer-field branches parse via `_to_int` (which does `int(float(...))`/similar) without guarding non-finite values before conversion, e.g. `KEY_TS_NO_OF_GIRDERS` branch around L191–199 uses `self._to_int(...)`.

**Suggested fix (diff idea)**
Reject non-finite values before integer conversion (in `_to_int` and/or per-field checks):
```diff
 def _to_int(self, value):
-    try:
-        return int(float(value))
-    except Exception:
-        return None
+    try:
+        v = float(value)
+    except Exception:
+        return None
+    if not math.isfinite(v):
+        return None
+    return int(v)
```
(Ensure callers return an appropriate validation message when parsed value is `None` due to non-finite input.)

**Duplicate check**
Searched refreshed issues (open+closed, `notes/issues_raw.json` through #129 context / refreshed this session) via `scripts/search_issues.py` for `OverflowError` and `infinity` — no matching issue found. #88 covers NaN/nonfinite acceptance in different context; this is an uncaught exception on `inf` for specific integer validators.

**Logs / proof**
- `scripts/validator_fuzz.py`
- `evidence/logs/trackF_validator_fuzz.txt`
- `evidence/logs/trackF_validator_fuzz.json`
