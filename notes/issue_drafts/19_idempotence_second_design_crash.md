# [Bug/Crash] Second `design()` call on the same object crashes in LTB buckling check (`math domain error`)

**Environment**
- OsdagBridge `dev` @ `d74f56d` (2026-07-26)
- macOS (Intel), conda env `osdagbridge-env`, Python 3.12.16
- Headless: `PlateGirderBridge().set_input(d); design(); design()` on the SAME object (proper `__main__` guard; no harness re-exec)
- Finding type: **T1 (confirmed crash — executed)**

**Scenario — what we filled (exact inputs)**
Default bridge built from `BASIC_INPUT_DICT` + `solve_extend_basic_input_dict` + material priming, no fields invented: span 30.0 m, carriageway 10.5 m, skew 0°, footpath None, median No, design mode Optimized, default materials (E 350A, M40). Layout solver gives 7 girders @ 2.28 m, D = 1.67 m. This is the normal case that completes fine on its own (SW01/SMOKE, ~70–130 s).

**What we got (executed, `dictionaries/IDEM2/same.log`, `evidence/logs/determinism_2.log`)**
- `design()` call #1 → **RUN1_DONE**, completes normally (max_DCR 1.871, as in the standalone case).
- `design()` call #2 on the same object → **crash**:
```
Traceback (most recent call last):
  File ".../same.py", line 11, in <module>
    b.design(); o2=...
  File ".../plategirderbridge.py", line 757, in design
    self._run_stage("5", self._run_dcr_checks, dataset)
  File ".../designer.py", line 1802, in compute_all
    ltb = self.compute_buckling_resistance(...)
  File ".../designer.py", line 1007, in compute_buckling_resistance
    res = IRC22_2014.cl_603_3_3_1_buckling_resistance_moment(...)
  File ".../irc22_2015.py", line 639, in cl_603_3_3_1_buckling_resistance_moment
    lambda_LT = math.sqrt(beta_b * (Zp * fy) / Mcr)
ValueError: math domain error
```
Stage 5 (DCR checks) → LTB buckling resistance. Exit code 1.

**Expected vs actual (the mistake)**
- **Expected:** calling `design()` twice on the same object (as happens when a user unlocks inputs and clicks Design again in the same session) should either produce consistent results or be explicitly reset — it should not crash.
- **Actual:** the second call crashes with `math domain error`, i.e. the argument to `sqrt` in the LTB check went negative/zero on the second run. Some state from run 1 is not reset before run 2 (the design() start calls `self.memory.release()` but section/DTO state appears to persist).

**Root cause (file:line, read-only)**
`src/osdagbridge/core/utils/codes/irc22_2015.py:639`:
```py
term1 = (math.pi ** 2 * E * Iy) / (LLT ** 2)
term2 = (G * It) + (math.pi ** 2 * E * Iw) / (LLT ** 2)
Mcr = math.sqrt(term1 * term2)  # Nmm
lambda_LT = math.sqrt(beta_b * (Zp * fy) / Mcr)   # <-- L639 ValueError on 2nd run
```
Called from `designer.py:1007` (`compute_buckling_resistance`). On the second run one of `Zp`, `fy`, `Mcr` or `beta_b` takes a value that makes the radicand negative/zero — consistent with stale girder-section state carried over from run 1. Exact stale field under investigation.

**Logs and proof**
- `scripts/determinism_check.py` (with `__main__` guard), `dictionaries/IDEM2/same.py`, `dictionaries/IDEM2/same.log`
- `evidence/logs/determinism_2.log` (RUN1_DONE then ValueError), full traceback in `dictionaries/IDEM2/same.log` tail
- Note: an earlier unguarded harness (`dictionaries/IDEM/same.log`) showed a forkserver re-exec artifact; it was discarded. The report relies only on the guarded IDEM2 run.

**Suggested fix (diff idea)**
- Reset all per-run section/DTO/check state at the start of `design()` (not just OpenSees memory), or guard the LTB computation:
```diff
  # irc22_2015.py, before the sqrt
+ if Mcr <= 0 or (beta_b * Zp * fy) <= 0:
+     raise ValueError(f"Invalid LTB input on design run: Mcr={Mcr}, Zp={Zp}, fy={fy} — reset design state before reuse.")
  lambda_LT = math.sqrt(beta_b * (Zp * fy) / Mcr)
```
- Add an idempotence regression test: two consecutive `design()` calls on one object must not crash and must give equal outputs.

**Duplicate check**
Searched refreshed issues (open+closed, 131 items) via `scripts/search_issues.py` for `second run`, `math domain`, `Mcr`, `buckling resistance`, `redesign`: #85 (3D CAD not displayed after unlock/redesign) is the closest "second run in same session" issue but concerns CAD display and reports no design-error dialog; this is a hard crash in the 2nd `design()` at stage 5. **No duplicate found.**

**Notes**
Reported as T1 (confirmed crash) — executed with a guarded harness, reproducible, exact traceback. Related to the "reuse backend object" state area (#85, #125) but a distinct failure mode.
