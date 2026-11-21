# [Bug/Validation] Carriageway width validator treats Median = "No" as a median, so the suggested minimum is 7.5 m instead of 4.25 m

**Environment:** macOS 13.6 (Darwin 22.6.0), Python (conda env `osdagbridge-env`), OsdagBridge branch `dev`, commit `d74f56d`.

## Description
`BridgeInputValidator.validate_basic_inputs` decides whether a median is present in two different ways inside the same branch:
- `validator.py:46` uses a truthiness test, `min_w = CARRIAGEWAY_WIDTH_MIN_WITH_MEDIAN if median else CARRIAGEWAY_WIDTH_MIN`.
- `validator.py:49` uses an equality test, `assumed_lanes = 2 if median == 'Yes' else 1`.

The UI stores the median option as the string `"No"` or `"Yes"`. Any non-empty string is truthy, so for a missing carriageway width with Median = **No** the validator returns 7.5 m, which is the with-median minimum. The correct value is 4.25 m (`CARRIAGEWAY_WIDTH_MIN`).

**Works:** median `"Yes"` returns 7.5 m. An empty string or `None` returns 4.25 m.
**Fails:** median `"No"` (the normal UI value) returns 7.5 m. The string `"None"` also returns 7.5 m.

## Steps to reproduce
```python
from osdagbridge.core.bridge_types.plate_girder.validator import BridgeInputValidator
from osdagbridge.core.utils.common import KEY_CARRIAGEWAY_WIDTH, KEY_INCLUDE_MEDIAN
BridgeInputValidator().validate_basic_inputs(
    KEY_CARRIAGEWAY_WIDTH, {KEY_CARRIAGEWAY_WIDTH: None, KEY_INCLUDE_MEDIAN: "No"})
```
Script: `scripts/probe_median_fix.py`.

## Expected
`(4.25, "Carriageway width must be specified.")`. With no median the single-carriageway minimum applies (IRC 5:2015 Cl. 104.3.1, as cited in the code comment). Line 49 of the same branch already uses `median == 'Yes'`.

## Actual
`(7.5, "Carriageway width must be specified.")`. Reproduced in two fresh processes (`evidence/logs/probe_median_fix.log`). In the desktop app, clearing the Carriageway Width field with Median = No resets it to 7.5 (offscreen Qt check, `evidence/logs/l7_empty_field.log`).

## Root cause
`src/osdagbridge/core/bridge_types/plate_girder/validator.py:46`
```python
min_w = CARRIAGEWAY_WIDTH_MIN_WITH_MEDIAN if median else CARRIAGEWAY_WIDTH_MIN
```

## Suggested fix
```diff
-                min_w = CARRIAGEWAY_WIDTH_MIN_WITH_MEDIAN if median else CARRIAGEWAY_WIDTH_MIN
+                min_w = CARRIAGEWAY_WIDTH_MIN_WITH_MEDIAN if median == 'Yes' else CARRIAGEWAY_WIDTH_MIN
```
Applying this to a copy of the method returns 4.25 for "No" and 7.5 for "Yes" (`evidence/logs/probe_median_fix.log`, AFTER_FIX lines).

## Duplicate check
I searched all 124 issues (open and closed), titles and bodies, for median + carriageway + minimum/7.5 and for `include_median`/`if median`. The hits were #143, #134, #133, #132, #114 and #112. None of them is about the validator's median test.
