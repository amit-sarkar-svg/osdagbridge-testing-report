# Title
[Bug/Design] Bearing-zone web buckling check (Cl. 509.7.3.1) reports a capacity 69× the squash load — uses the stiffener's inertia and an uncapped Euler stress, so it always passes

# Description

## Environment
- OS: macOS 13.6 (Darwin 22.6.0)
- Python: conda env `osdagbridge-env`
- Branch: `dev`, commit `d74f56d`

## Description
The design check **"Brg.Stiff: Web Buckling" (Cl.509.7.3.1)** is meant, per its own comment, to check "if the *unstiffened* web bearing zone can carry R" (`designer.py:1665`). The calculation (`designer.py:1666-1671`):
```python
n1      = d / 2.0
A_wb    = (b1 + n1) * tw
rys_wb  = math.sqrt(Iys / A_wb)          # Iys = inertia of the two bearing-stiffener plates
KL_r_wb = KL / rys_wb
fcc_wb  = (math.pi**2 * E) / KL_r_wb**2  # Euler stress, not limited to fy
Fcdw_wb_kN = fcc_wb * A_wb / 1000.0
```
1. It divides the **stiffener** inertia `Iys` (line 1660) by the area of the **bare web** strip, giving a very large radius of gyration.
2. It uses the raw Euler stress with no limit at the yield stress and no buckling curve, although the stiffener column check next to it (`:1691`) uses the program's design compressive stress function.

## Steps to Reproduce
Span 20 m, carriageway 7.5 m, skew 0°, no footpath, no median, Optimized (`inputs/H_s20_params.json`) → Design → Design Checks → "Brg.Stiff: Web Buckling". Script: `scripts/probe_web_buckling.py <case_dir>`.

## Expected Behaviour
A compressive resistance can never exceed the squash load `A·fy/γm0`. For an unstiffened web strut (r = tw/√12, KL = 0.7 d as in the code) the program's own `IS800_2007.cl_7_1_2_1_design_compressisive_stress_plategirder` gives the realistic value.

## Actual Behaviour
| Quantity | Value |
|---|---|
| Reported stress fcc | **21 858.5 MPa** (62.5 × fy = 350 MPa) |
| Reported capacity | **109 506 kN** → PASS (R = 250 kN) |
| Squash load A·fy/γm0 (A = 5010 mm²) | 1 594 kN (reported is 68.7× this) |
| Program's own fcd for web strut (KL/r = 331) | 14.7 MPa → Fcdw = **73.8 kN < R = 250 kN → FAIL** |

Reproduced twice in separate fresh processes. The value is written to the output dictionary (`plategirderbridge.py:4260`) and the design-check list; it does not drive another decision (bearing stiffeners are checked separately), so the design itself is not made unsafe, but a physically impossible capacity is reported as PASS.

## Root Cause
`designer.py:1668-1670` (stiffener inertia with web area; Euler stress without the buckling curve or fy cap).

## Suggested Fix
```diff
-        rys_wb  = math.sqrt(Iys / A_wb) if A_wb > 0 else 0.0
-        KL_r_wb = KL / rys_wb if rys_wb > 0 else 1e9
-        fcc_wb  = (math.pi**2 * E) / KL_r_wb**2
+        rys_wb  = tw / math.sqrt(12.0)                       # unstiffened web strut
+        KL_r_wb = KL / rys_wb if rys_wb > 0 else 1e9
+        fcc_wb  = IS800_2007.cl_7_1_2_1_design_compressisive_stress_plategirder(fy, gm0, KL_r_wb, E)
         Fcdw_wb_kN = fcc_wb * A_wb / 1000.0
```
Applied to the H_s20 data this gives 73.8 kN (FAIL → "stiffener needed"), consistent with the stiffener actually being provided.

## Duplicate Check
Searched all 210 issues for web buckling / bearing stiffener / Fcdw / 509.7.3 / 8.7.3 / Euler. #156 (bearing length input ignored) and #173 (mode switch resets stiffener overrides) mention bearing stiffeners but not this check.
