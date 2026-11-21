# [Bug/Validation] Clearing the Skew Angle field silently sets skew to the minimum (-15°) instead of the default 0°

**Environment:** macOS 13.6 (Darwin 22.6.0), conda env osdagbridge-env, branch dev, commit d74f56d, Qt offscreen.

**Description:** When the Skew Angle line edit is empty and loses focus, `InputDock._on_field_edited` (input_dock.py:949-986) calls `validate_basic_inputs`. For a missing value `validator.py:63-64` returns `SKEW_ANGLE_MIN` (-15.0) as the "corrected" value, and the widget and `input_dict` are overwritten with `-15.0`. The popup only says "Skew angle must be a numeric value.", so the user does not learn that a 15° skew was chosen. `SKEW_ANGLE_DEFAULT = 0.0` exists in common.py:332 and keyfile.py:68 but is never used in the source. Because skew-sign handling is not mirror-symmetric (#132), -15° is also the more unfavourable side.
Works: valid number typed (e.g. 5). Fails: empty field.

**Steps:** run `scripts/l7_empty_field.py` (offscreen), or by hand: clear Skew Angle, press Tab.
**Expected:** reset to 0.0 (`SKEW_ANGLE_DEFAULT`), or leave the field flagged without changing the value.
**Actual:** text `-15.0`, `input_dict['geometry.skew_angle'] == '-15.0'` (2 fresh processes, `evidence/logs/l7_empty_field.log`). Span (empty -> 20.0) and carriageway (empty -> 7.5) are replaced the same way by the lower limit; these may be intended, skew is the clearest because a default exists.

**Root cause:** validator.py:63-64 `return SKEW_ANGLE_MIN, "Skew angle must be a numeric value."`
**Suggested fix:**
```diff
-            if skew_angle is None:
-                return SKEW_ANGLE_MIN, "Skew angle must be a numeric value."
+            if skew_angle is None:
+                return SKEW_ANGLE_DEFAULT, "Skew angle must be a numeric value."
```
Proof: with that behaviour patched in (scripts/l7_empty_skew_fix.py) the empty-field result is 0.0 (`evidence/logs/l7_empty_skew_fix.log`).
**Duplicate check:** searched issue titles/bodies for skew + empty/blank/numeric value/SKEW_ANGLE_MIN: #199, #112, #111, #88, #85, #45 (none cover this).
