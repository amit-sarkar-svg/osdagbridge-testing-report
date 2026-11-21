# Proof — #88: Extra trigger for #88: validate_basic_inputs / validate_material_inputs accept NaN and bool

**Issue:** https://github.com/Nidhikhare12/OsdagBridge/issues/88  
**Severity:** S2 · Medium · **Tier:** T4 (existing issue)  
**Environment:** OsdagBridge `dev` @ `d74f56d` · macOS 13.6 (Darwin 22.6.0) · conda env `osdagbridge-env` · tested 2026-11-21

## Reproduce
```bash
source ~/miniconda3/etc/profile.d/conda.sh && conda activate osdagbridge-env
cd osdagbridge-testing-report
python proofs/088_comment_nan_accepted_by_validators/scripts/probe_cands1.py
```

## Expected
NaN, `"nan"` and `True` rejected.

## Actual
span/skew/carriageway/Fy = NaN → `None` (valid); skew `True` → valid; `validate_map_coordinates('999','nan')` → `(True,'')` (see #180).

## Evidence in this folder
| File | What it shows |
|---|---|
| `logs/probe_cands1.log, logs/probe_cands1_run2.log` | Two fresh processes, identical |

## Root cause
`validator.py:1094-1097` `_to_float` uses `float()`; every `<`/`>` comparison with NaN is False.

## Notes
Comment material for existing issues #88 and #180. The OsdagBridge clone was never modified; fixes were proven by monkeypatching a copy inside the test scripts. The issue or comment text as drafted is in `COMMENT_088.md`.
