# [Bug/Validation] `validate_additional_inputs` accepts NaN/inf for ALL additional input keys

**Environment**
- OsdagBridge `dev` @ `d74f56d` (2026-07-26)
- macOS (Intel), conda env `osdagbridge-env`, Python 3.12.16
- Executed headless via `scripts/osi_sweep.py` (9299 cases: 547 keys × 17 value classes)
- Finding type: **T2 (likely bug — executed and reproduced)**

**Description**
`BridgeInputValidator.validate_additional_inputs()` accepts `NaN` and `±inf` values for ALL keys in `_ADDITIONAL_KEYS` without rejecting them. The validator calls `self._to_float(inputs.get(key))`, which returns `float('nan')` or `float('inf')` for non-numeric/non-finite string inputs, but the subsequent range checks (`v < min`, `v > max`) always evaluate to `False` for NaN/inf, so the invalid value passes through uncorrected.

**Steps / Reproduction (executed)**
Run `scripts/osi_sweep.py` which iterates all 547 flattened keys from `test_cases/baseline.osi` × 17 value classes, calling `validate_osi_inputs()` (which calls `validate_additional_inputs` for each key in `_ADDITIONAL_KEYS`).

Key examples of out-of-range values ACCEPTED (validator returns "valid", no error):

| Key | Value | Expected | Actual |
|-----|-------|----------|--------|
| `typical_section.girder_spacing` | `nan` | REJECT (out of range [0.5, overall/2]) | ACCEPTED (valid) |
| `typical_section.no_of_girders` | `inf` | REJECT (out of range [2, ceil(2*overall)]) | ACCEPTED (valid) |
| `typical_section.no_of_girders` | `-inf` | REJECT (out of range [2, ceil(2*overall)]) | ACCEPTED (valid) |
| `typical_section.deck_overhang` | `nan` | REJECT (out of range [0.0, overall/2]) | ACCEPTED (valid) |
| `typical_section.deck_thickness` | `nan` | REJECT (out of range [100, 500]) | ACCEPTED (valid) |
| `typical_section.footpath_width` | `nan` | REJECT (out of range [min, carriageway_width]) | ACCEPTED (valid) |
| `typical_section.crash_barrier.width` | `nan` | REJECT (out of range [0.0, overall/2]) | ACCEPTED (valid) |

All 17 `_ADDITIONAL_KEYS` accept `NaN`, and 16 of them also accept `inf`/`-inf`. Only `KEY_TS_GIRDER_SPACING` correctly rejects `inf` (because `inf > max_gs` is `True`), but accepts `nan` (because `nan < 0.5` is False and `nan > max_gs` is also False).

**Expected vs actual**
- **Expected:** `validate_additional_inputs` should reject NaN and ±inf values with a "must be a numeric value" or out-of-range error, just as `validate_basic_inputs` correctly rejects `geometry.span=inf`.
- **Actual:** `validate_additional_inputs` accepts NaN/inf for all 17 keys in `_ADDITIONAL_KEYS`, returning `None` (valid) instead of a correction message.

**Root cause (file:line, read-only)**
`src/osdagbridge/core/bridge_types/plate_girder/validator.py`, method `validate_additional_inputs` (≈L174). The method calls `self._to_float(inputs.get(key))` which returns `float('nan')` or `float('inf')` for non-numeric/non-finite string inputs. The subsequent range checks (`v < min`, `v > max`) always evaluate to `False` for NaN/inf (NaN comparisons are always False; `inf > max_gs` is True only when max_gs is finite, but for keys without a derived `max_gs` like `deck_thickness`, there's no upper bound check at all).

**Logs / proof**
- `scripts/osi_sweep.py`, `evidence/logs/w4_osi_sweep.log`, `test_cases/os_sweep_results.csv` (9299 cases)
- Key evidence: 17 keys in `_ADDITIONAL_KEYS` accept NaN; 16 of them also accept inf/-inf

**Suggested fix (diff idea)**
Add NaN/inf rejection in `validate_additional_inputs` (or in `_to_float`):

```diff
     v = self._to_float(inputs.get(key))
+    if v is not None and (math.isnan(v) or math.isinf(v)):
+        return v, f"{key} must be a finite numeric value."
     if v is None: return <corrected>, "... must be a numeric value."
```

**Duplicate check**
Searched existing OsdagBridge issues (open+closed, 83 issues, max #146) via `scripts/search_issues.py` for `validate_additional_inputs`, `NaN`, `inf`, `cross_bracing`, `end_diaphragm`:
- **#88** "[Bug] OSI validation accepts NaN physical inputs before layout and model construction" — lists `geometry.span=NaN`, `geometry.skew_angle=NaN`, `geometry.carriageway_width=NaN`, `material.girder.e=NaN`, `material.deck.ecm=NaN` as accepted. #88 covers specific keys in `_BASIC_KEYS` and material keys NOT in any validation list. It does NOT cover keys in `_ADDITIONAL_KEYS` like `typical_section.girder_spacing`, `typical_section.no_of_girders`, etc.
- No existing issue covers `validate_additional_inputs` accepting NaN/inf for ALL keys in `_ADDITIONAL_KEYS`.

**Notes**
Reported as T2 (likely bug — executed and reproduced with 9299 cases). This extends #88 which covers specific keys in `_BASIC_KEYS` and material keys not in any validation list; this finding extends to ALL keys in `_ADDITIONAL_KEYS` that are validated by `validate_additional_inputs`.
