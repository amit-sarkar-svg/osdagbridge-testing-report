# Proof — #135: Root cause for #135: design() converts girder dimensions mm→m in place, so a second design() divides again

**Issue:** https://github.com/Nidhikhare12/OsdagBridge/issues/135  
**Severity:** S2 · Medium · **Tier:** T4 (existing issue) + root cause  
**Environment:** OsdagBridge `dev` @ `d74f56d` · macOS 13.6 (Darwin 22.6.0) · conda env `osdagbridge-env` · tested 2026-11-21

## Reproduce
```bash
source ~/miniconda3/etc/profile.d/conda.sh && conda activate osdagbridge-env
cd osdagbridge-testing-report
python proofs/135_comment_root_cause_double_mm_to_m/scripts/probe_double_convert.py
```

## Expected
A second `design()` on the same object gives the same result as the first.

## Actual
Depth 1670 mm → 1.67 m after run 1 → 0.00167 m in run 2, then `ValueError: math domain error` (LTB check).

## Evidence in this folder
| File | What it shows |
|---|---|
| `logs/probe_double_convert_1.log, logs/probe_double_convert_2.log` | Two fresh processes, identical |
| `logs/probe_double_convert_fix.log` | Fix proof: pristine deep copy restored before each design() → run 1 = run 2 = 1.67, no crash |
| `logs/probe_ui_path_alias.log` | Desktop path (set_input before each design) does not crash for this input |
| `inputs/A1_params.json` | Input: span 30, carriageway 15, skew 0, no footpath/median, Optimized |

## Root cause
`plategirderbridge.py:536-589` (`_convert_girder_dims_mm_to_m`) divides `self.input_dict` values in place; called on every `design()` at line 683.

## Notes
Prepared as a comment for the existing issue, not as a new issue. The OsdagBridge clone was never modified; fixes were proven by monkeypatching a copy inside the test scripts. The issue or comment text as drafted is in `COMMENT_135.md`.
