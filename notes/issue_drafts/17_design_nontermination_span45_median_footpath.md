# [Bug/Performance] Valid inputs (span 45 m + median + footpaths) make `design()` run >10 minutes without completing

**Filed:** [Nidhikhare12/OsdagBridge#133](https://github.com/Nidhikhare12/OsdagBridge/issues/133) — open (filed 2026-11-17)

**Environment**
- OsdagBridge `dev` @ `d74f56d` (2026-07-26)
- macOS (Intel), conda env `osdagbridge-env`, Python 3.12.16
- Headless design via `PlateGirderBridge().set_input(d); design()` from `BASIC_INPUT_DICT` + `solve_extend_basic_input_dict` + material priming (no GUI, no baseline.osi)
- Finding type: **T2 (likely performance/hang bug)**

**Scenario — what we filled (exact inputs)**
All inputs from the app's own default flow; only these were changed:

| Field | SW03 value | SW06 value |
|---|---|---|
| geometry.span | 45.0 m | 45.0 m |
| geometry.carriageway_width | 15.0 m | 15.0 m |
| geometry.skew_angle | −15.0° | +15.0° |
| geometry.footpath | Both Sides | Single Side |
| geometry.include_median | Yes | Yes |
| geometry.design_mode | Optimized | Optimized |
| materials | defaults (E 350A, M40) | defaults |

All values are within the documented limits (span ≤45, cw ≤23.6, skew ±15, median only with cw≥7.5). The bridge is geometrically valid.

**What we got (executed)**
- SW03: `design()` did **not** finish within the 600 s (10-min) per-case timeout — killed at 600.2 s (`evidence/logs/design_sweep_run.log`, `dictionaries/SW03/case.log`, `dictionaries/SW03/result.json` absent). A second run with no timeout consumed **>12 min CPU** and still produced no result before being stopped (`evidence/logs/SW03_rerun.log`).
- SW06 (same span/cw/median, skew +15, footpath Single Side): also timed out at 600.1 s.
- The SW03 case log stalls after repeated `UserWarning: ... 'thermal_load' load case not available` and shows earlier `RuntimeWarning: The iteration is not making good progress ... fsolve` from `ospgrillage/utils.py:555`, i.e. the run is stuck in the analysis/envelope stage, not producing output.
- **Controls that complete normally** (same harness): span 30/cw 10.5/no median/no footpath = 71–79 s; span 45/cw 10.5/no median/no footpath (`OR_SPAN45`) = 77.5 s; span 30/cw 15 = 100 s; span 30 + footpath Both Sides = 121 s. So the slow/hanging cases are specifically the combination of **max span (45 m) + median + footpaths**.

**Expected vs actual (the mistake)**
- **Expected:** a valid input within documented limits should complete in a time comparable to other valid cases (tens of seconds to a couple of minutes), or raise a clear error.
- **Actual:** `design()` runs indefinitely (>10 min, no result) for these valid inputs, so a user pressing Design would see the app hang with no result.

**Logs and proof**
- `scripts/design_sweep.py`, `scripts/design_runner.py`, `test_cases/built/SW03.params.json`, `SW06.params.json`
- `evidence/logs/design_sweep_run.log` (SW03/SW06 timeout lines), `evidence/logs/SW03_rerun.log`, `dictionaries/SW03/case.log`, `dictionaries/SW06/case.log`
- Controls: `dictionaries/SMOKE/result.json`, `dictionaries/OR_SPAN45/result.json`, `evidence/logs/oracle_runs3.log`

**Likely area (root cause not pinned)**
Analysis/moving-load envelope stage: `ospgrillage/utils.py:555` `fsolve` non-convergence on the oblique grillage with many components (median + both footpaths) at the maximum span; the repeated `'thermal_load' load case not available` warnings indicate stage 4F/4G. Exact line under investigation.

**Suggested fix (direction)**
- Bound the moving-load/envelope solver (iteration cap / tolerance) so non-convergent cases terminate with a clear warning instead of hanging.
- Investigate why median + footpaths at max span prevents convergence; add a regression test with this input that must complete within a time budget.

**Duplicate check**
Searched open+closed issues (refreshed `notes/issues_raw.json`, 131 items) via `scripts/search_issues.py` for `hang`, `slow`, `timeout`, `non-converg` — no matching issue about `design()` hanging on valid span-45 + median/footpath inputs. **No duplicate found.**

**Notes**
Reported as T2 (likely): reproduced twice (SW03 twice, SW06 once) and controls complete quickly; but it is a performance/non-termination issue rather than a wrong numeric result.
