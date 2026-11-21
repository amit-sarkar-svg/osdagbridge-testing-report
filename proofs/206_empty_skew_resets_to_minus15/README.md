# Proof — #206: Clearing the Skew Angle field silently sets skew to -15° instead of the default 0°

**Issue:** https://github.com/Nidhikhare12/OsdagBridge/issues/206  
**Severity:** S2 · Medium · **Tier:** T1 confirmed  
**Environment:** OsdagBridge `dev` @ `d74f56d` · macOS 13.6 (Darwin 22.6.0) · conda env `osdagbridge-env` · tested 2026-11-21

## Reproduce
```bash
source ~/miniconda3/etc/profile.d/conda.sh && conda activate osdagbridge-env
cd osdagbridge-testing-report
python proofs/206_empty_skew_resets_to_minus15/scripts/l7_empty_field.py
python proofs/206_empty_skew_resets_to_minus15/scripts/proof_ui_screens.py /tmp/ui_screens
```

## Expected
Skew field resets to `0.0` (`SKEW_ANGLE_DEFAULT`, common.py:332), or is flagged without being changed.

## Actual
Skew field and `input_dict['geometry.skew_angle']` become `-15.0`; popup only says *"Skew angle must be a numeric value."*

## Evidence in this folder
| File | What it shows |
|---|---|
| `screenshots/01_before.png` | Input dock before: span 30, carriageway 10, median No, skew 5 |
| `screenshots/02_after_clearing_skew.png` | After clearing Skew Angle and leaving the field: shows **-15.0** |
| `logs/l7_empty_field.log` | Two fresh processes, identical result (span→20.0, skew→-15.0, carriageway→7.5) |
| `logs/proof_ui_screens.log` | Values read back from the dock while the screenshots were taken |
| `logs/l7_empty_skew_fix.log` | Fix proof: validator patched to return `SKEW_ANGLE_DEFAULT` → field becomes 0.0 |
| `logs/l7_ui_probe.log` | Supporting: typed `nan`/`inf`/`1e999` are blocked or corrected by `QDoubleValidator` (checked & correct) |
| `inputs/empty_skew_field.json` | Scenario definition |

## Root cause
`validator.py:63-64` returns `SKEW_ANGLE_MIN` for a missing value.

## Notes
Test runs offscreen (`QT_QPA_PLATFORM=offscreen`) on the real `CustomWindow`/`InputDock`; only the modal message box is replaced by a recorder so the test does not block. The OsdagBridge clone was never modified; fixes were proven by monkeypatching a copy inside the test scripts. The issue or comment text as drafted is in `ISSUE_206.md`.
