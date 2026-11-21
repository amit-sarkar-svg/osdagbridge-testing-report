# Proof — #209: PlateGirderBridge._lookup_material returns None for an unknown grade and raises IndexError for an empty name

**Issue:** https://github.com/Nidhikhare12/OsdagBridge/issues/209  
**Severity:** S3 · Low · **Tier:** T1 confirmed  
**Environment:** OsdagBridge `dev` @ `d74f56d` · macOS 13.6 (Darwin 22.6.0) · conda env `osdagbridge-env` · tested 2026-11-21

## Reproduce
```bash
source ~/miniconda3/etc/profile.d/conda.sh && conda activate osdagbridge-env
cd osdagbridge-testing-report
python proofs/209_lookup_material_returns_none/scripts/probe_cands3.py
```

## Expected
A float (per the `-> float` annotation and the docstring's fallback promise) or a clear `LookupError`.

## Actual
`('E 999','Yield Strength')` → `None`; `('', 'Yield Strength')` → `IndexError: string index out of range`.

## Evidence in this folder
| File | What it shows |
|---|---|
| `logs/probe_cands3.log` | Run 1 |
| `logs/probe_cands3_run2.log` | Run 2 in a fresh process, identical |

## Root cause
`plategirderbridge.py:1124-1167`: no return/raise after a missing row; `material_name[0]` on an empty string; error message formats the class `sqlite3.Error` instead of the exception.

## Notes
Low reachability from the GUI (grades come from a dropdown); relevant for hand-edited or stale `.osi` files. The OsdagBridge clone was never modified; fixes were proven by monkeypatching a copy inside the test scripts. The issue or comment text as drafted is in `ISSUE_209.md`.
