# [Bug/Analysis] Valid input silently skips live load → all design demands = 0 and verdict PASS (wrong PASS)

**Filed:** [Nidhikhare12/OsdagBridge#134](https://github.com/Nidhikhare12/OsdagBridge/issues/134) — open (filed 2026-11-17)

**Environment**
- OsdagBridge `dev` @ `d74f56d` (2026-07-26)
- macOS (Intel), conda env `osdagbridge-env`, Python 3.12.16
- Headless design via `PlateGirderBridge().set_input(d); design()` from `BASIC_INPUT_DICT` + `solve_extend_basic_input_dict` + material priming (no GUI, no baseline.osi)
- Finding type: **T1 (confirmed wrong PASS — executed and reproduced)**

**Scenario — what we filled (exact inputs, case SW05 / repro P5_SW05R)**
All values from the app's own default flow; only these changed:

| Field | Value |
|---|---|
| structure.type | Highway Bridge |
| geometry.span | 30.0 m |
| geometry.carriageway_width | **7.5 m** (minimum allowed with median) |
| geometry.skew_angle | 0.0° |
| geometry.footpath | **Both Sides** |
| geometry.include_median | **Yes** |
| geometry.design_mode | Optimized |
| materials | defaults (E 350A, M40) |

All inputs are within documented limits (median allowed only with cw ≥ 7.5 m — satisfied). The bridge is geometrically valid.

**What we got (executed output, `dictionaries/P5_SW05R/output.json`, `dictionaries/SW05/output.json`)**
- Root warning in log: `analyser.py:1998 UserWarning: Envelope-based governing LL detection failed ("not all values found in index 'Element'. Try setting the method keyword argument (example: method='nearest')."); skipping LL creation.` followed by 26× `'live_load'/'thermal_load' load case not available` warnings.
- Design check table:
  - `ULS Flexure  0.00 / 11498.55 → 0.000 PASS`
  - `ULS Shear  0.00 → 0.000 PASS`, `M-V Interaction 0.000 PASS`
  - `steeldesign.details.moment.mu_applied = 0.0` (compare normal cases ≈ 2600 kN·m)
  - all `util.* = 0.0`
- **OVERALL VERDICT: Status PASS, Maximum DCR 0.2853** (the only nonzero/failing check is a stiffener check `Int.Stiff: Leg ≤ H_limit = 1.479 FAIL`, which is excluded from the structural DCR set — so the design is reported as PASS).

**Controls (same build method, only one field changed — all show 0 warnings and normal demands)**
- `P5_MED_NOFOOT` (median Yes, footpath None): `mu_applied = 2943.66`, flexure 25.4%, fatigue 206.8% — 0 live-load warnings.
- `P5_FOOT_NOMED` (footpath Both Sides, median No): `mu_applied = 2652.52`, flexure 22.9%, fatigue 186.3% — 0 warnings.
- `P5_MED_CW105` (median Yes + Both Sides, cw 10.5 m): 0 live-load warnings.
So the trigger is specifically the **combination of median Yes + Both Sides footpath + cw exactly 7.5 m + zero skew**; each near-neighbor works.

**Expected vs actual (the mistake)**
- **Expected:** a valid bridge with live load present must have nonzero flexure/shear demand and a realistic utilisation; if live-load detection genuinely fails, the design should abort with a clear error, not report PASS.
- **Actual:** live-load case creation silently fails (a caught `KeyError`-type xarray `.sel` error), the ULS envelope is built with zero vehicle load, all structural demands become 0, and the design is reported **PASS** — a dangerously unconservative result for a bridge design tool.

**Logs and proof**
- `scripts/design_runner.py`, `scripts/oracle_runs.py`, `test_cases/built/SW05.params.json`, `test_cases/built/P5_SW05R.input.json`
- `dictionaries/SW05/case.log` (root warning + 26 live-load warnings), `dictionaries/P5_SW05R/run.log`
- `dictionaries/P5_SW05R/output.json` (mu=0.0, all utils 0.0), controls `dictionaries/P5_MED_NOFOOT/output.json`, `dictionaries/P5_FOOT_NOMED/output.json`
- `evidence/logs/design_sweep_run.log` (SW05 ok, 132.8 s)

**Root cause (file:line, read-only)**
`src/osdagbridge/core/bridge_types/plate_girder/analyser.py:1988-2003` in `create_governing_ll_load_case()`:
```py
gov_element = env_val.idxmax("Element").item()
governing_lc = str(env_lc.sel(Element=gov_element).values)   # <-- L1991 KeyError when the governing
                                                             #     element id is absent from env_lc's
                                                             #     'Element' index (median/footpath layout)
...
except Exception as exc:
    warnings.warn(f"Envelope-based governing LL detection failed ({exc}); skipping LL creation.")
    self.ll_load_case = None        # <-- L1998: LL case never created
    return dataset
```
Then `create_dl_ll_combination()` (≈L2100) warns `live-load case not available` and builds a combo with no LL; with no ULS load case, the design envelope reports zero flexural/shear demand. The broad `except Exception` swallows the lookup error and continues as PASS.

**Suggested fix (diff idea)**
```diff
-            governing_lc = str(env_lc.sel(Element=gov_element).values)
+            try:
+                governing_lc = str(env_lc.sel(Element=gov_element, method="nearest").values)
+            except KeyError:
+                # fall back to a nearest-element lookup or raise a clear error
+                governing_lc = str(env_lc.sel(Element=gov_element, method="nearest").values)
@@
-        except Exception as exc:
-            warnings.warn(f"Envelope-based governing LL detection failed ({exc}); skipping LL creation.")
-            self.ll_load_case = None
-            return dataset
+        except Exception as exc:
+            raise RuntimeError(
+                "Governing live-load detection failed; refusing to produce a design with zero live load."
+            ) from exc
```
At minimum, do not silently continue to a PASS verdict when the governing LL case cannot be determined — fail loudly.

**Duplicate check**
Searched refreshed issues (open+closed, 131 items) via `scripts/search_issues.py`: #87 (seismic uses zero LL mass because it runs before governing-vehicle selection) and #45 (missing DCR categories written as 0.0 on output dock) are related but have different triggers; #92 is thermal load cases. **No duplicate found for "governing LL detection fails → all ULS demand zero → PASS".**

**Notes**
Reported as T1 (confirmed) because the wrong PASS is executed and reproduced (SW05 and P5_SW05R) with the exact input isolated and near-neighbor controls showing nonzero demands.

**Update (2026-11-17, after filing):** a second, very different valid input reproduces the same bug — SW15: span 45 m, cw 23.6 m, skew −7.5°, no median/footpath → same `Element` index error, `mu_applied=0.0`, verdict PASS. So the trigger is broader than the filed title suggests; see comment draft `notes/issue_drafts/18b_comment_issue134_more_wrong_pass_triggers.md` (posted status: pending).
