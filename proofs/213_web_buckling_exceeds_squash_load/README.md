# Proof — #213: Bearing-zone web buckling check (Cl. 509.7.3.1) reports a capacity 69× the squash load

**Issue:** https://github.com/Nidhikhare12/OsdagBridge/issues/213  
**Severity:** S2 · Medium (physically impossible capacity reported as PASS; report-only) · **Tier:** T1 confirmed  
**Environment:** OsdagBridge `dev` @ `d74f56d` · macOS 13.6 (Darwin 22.6.0) · conda env `osdagbridge-env` · tested 2026-11-21

## Reproduce
```bash
source ~/miniconda3/etc/profile.d/conda.sh && conda activate osdagbridge-env
cd osdagbridge-testing-report
# Design for span 20 m (saved state goes to dictionaries/s12/H_s20/)
python proofs/211_static_vehicles_fixed_at_x0/scripts/batch_design.py test_cases/generated/s12_cases.json dictionaries/s12
python proofs/213_web_buckling_exceeds_squash_load/scripts/probe_web_buckling.py dictionaries/s12/H_s20
```
Input: `inputs/H_s20_params.json` (span 20 m, carriageway 7.5 m, skew 0°, no footpath, no median, Optimized).

## Expected
No compressive resistance can exceed the squash load `A·fy/γm0`. According to the code's own comment (`designer.py:1665`), the check is for the *unstiffened* web bearing zone. For an unstiffened web strut (r = tw/√12), the program's own `IS800_2007.cl_7_1_2_1_design_compressisive_stress_plategirder` gives the realistic capacity.

## Actual
| Quantity | Value |
|---|---|
| Radius of gyration used `rys_wb` | **80.1 mm** (from stiffener inertia `Iys` ÷ web area). Web alone: tw/√12 = 2.31 mm |
| Reported stress `fcc_wb` | **21 858.5 MPa** (62.5 × fy = 350 MPa) |
| Reported capacity | **109 506 kN → PASS** (R = 250.02 kN) |
| Squash load A·fy/γm0 (A = 5010 mm²) | 1 594 kN; the reported value is 68.7× this |
| Program's own fcd for the web strut (KL/r = 331) | 14.74 MPa → Fcdw = **73.8 kN < R → FAIL** |

Reproduced twice in separate fresh processes (`logs/probe_web_buckling.log`). The program uses KL = 761.6 mm, and the probe uses 0.7·d = 764.4 mm. This difference has no effect on the conclusion.

## Evidence in this folder
| File | What it shows |
|---|---|
| `logs/probe_web_buckling.log` | Two runs: reported fcc and capacity, squash limit, web-strut capacity with the program's own function |
| `report_output/web_buckling_extract.json` | The exact check entry ("Brg.Stiff: Web Buckling", Cl.509.7.3.1, PASS, 109506.26 kN) and `capacity_details.bearing_stiffener` (`rys_wb_mm` 80.144, `fcc_wb_MPa` 21858.5, `Fcdw_wb_kN` 109506.3) from the saved design state |
| `inputs/H_s20_params.json` | Exact input |
| `scripts/probe_web_buckling.py`, `scripts/design_runner.py` | Probe, and the input builder used by the batch run |

## Root cause
`designer.py:1668-1670`: `rys_wb = sqrt(Iys / A_wb)` mixes the stiffener's inertia with the web's area, and `fcc_wb = π²E/(KL/r)²` is the raw Euler stress, with no fy cap and no buckling curve. The stiffener column check next to it (`:1691`) does use the design compressive-stress function.

## Notes
The value appears in the design-check list and output dictionary (`plategirderbridge.py:4260`) but does not drive another decision, because bearing stiffeners are checked separately. The OsdagBridge clone was never modified. The issue text as posted is in `ISSUE_213.md`.
