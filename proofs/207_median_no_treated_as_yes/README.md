# Proof — #207: Carriageway width validator treats Median = "No" as a median (7.5 m instead of 4.25 m)

**Issue:** https://github.com/Nidhikhare12/OsdagBridge/issues/207  
**Severity:** S2 · Medium · **Tier:** T1 confirmed  
**Environment:** OsdagBridge `dev` @ `d74f56d` · macOS 13.6 (Darwin 22.6.0) · conda env `osdagbridge-env` · tested 2026-11-21

## Reproduce
```bash
source ~/miniconda3/etc/profile.d/conda.sh && conda activate osdagbridge-env
cd osdagbridge-testing-report
python proofs/207_median_no_treated_as_yes/scripts/probe_median_fix.py
```

## Expected
`(4.25, 'Carriageway width must be specified.')` for Median = No (single-carriageway minimum, IRC 5:2015 Cl. 104.3.1 as cited in the code).

## Actual
`(7.5, ...)` for Median = `"No"`; in the UI the cleared field is reset to **7.5**.

## Evidence in this folder
| File | What it shows |
|---|---|
| `screenshots/03_after_clearing_carriageway_median_no.png` | Median = No, carriageway cleared → field reset to **7.5** |
| `screenshots/01_before.png` | State before clearing |
| `logs/probe_median_fix.log` | BEFORE lines (two processes): No→7.5, Yes→7.5, ''→4.25, None→4.25; AFTER_FIX lines: No→4.25, Yes→7.5 |
| `logs/probe_cands1.log, logs/probe_cands1_run2.log` | Same result in the broader validator probe (identical in two processes) |
| `logs/proof_ui_screens.log` | Values read back from the dock |

## Root cause
`validator.py:46` uses `if median` (truthy for the string "No"), while line 49 of the same branch uses `median == 'Yes'`.

## Notes
Fix proof applies the one-token change to a copy of the method (no edit of the OsdagBridge repo). The OsdagBridge clone was never modified; fixes were proven by monkeypatching a copy inside the test scripts. The issue or comment text as drafted is in `ISSUE_207.md`.
