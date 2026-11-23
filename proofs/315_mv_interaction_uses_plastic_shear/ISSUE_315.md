# Title
[Bug/Design] M-V interaction is fed the plastic shear capacity instead of the governing shear buckling resistance, so high shear never reduces the moment capacity (shear DCR 0.76 still gives beta = 0)

# Description

## Environment
- OS: macOS 13.6 (Darwin 22.6.0)
- Python: conda env `osdagbridge-env`
- Branch: `dev`, commit `d74f56d`

## Description
IRC 22:2015 Cl. 603.3.3.3 (IS 800:2007 Cl. 9.2.2) reduces the design bending strength when `V > 0.6·Vd`, where `Vd` is the **design shear strength**, i.e. the lower of web yielding and web shear buckling. For a plate girder with a slender web the buckling value governs.

The code computes both:
- `results.Vd_kN` — plastic shear capacity, from `compute_shear_capacity()` (`designer.py:1762`);
- `results.Vcr_kN` — shear buckling resistance, from `compute_shear_buckling()` (`designer.py:1785`).

`Vcr` is the one the program itself treats as the shear capacity: the "ULS Shear Buckling" check and the report's "Girder — Shear" row both use it. But the M-V interaction is called with the plastic value (`designer.py:1826`):

```python
self.compute_combined_bending_shear(results.Md_kNm, Vu_kN, results.Vd_kN)
```

So the high-shear threshold becomes `0.6·Vd_plastic` instead of `0.6·Vcr`. For the case below that is 1193.9 kN instead of 265.8 kN — a factor of 4.5 — so the moment capacity is never reduced in the range where the code reports the shear utilisation as 0.6 to 1.0.

## Steps to Reproduce
1. Inputs: span 25 m, carriageway 7.5 m, skew 0°, no footpath, **median = Yes**, Optimized.
2. Run Design.
3. Compare the "ULS Shear Buckling" check (demand/capacity) with the "M-V Interaction" check and `beta_interaction`.

## Expected Behaviour
With `Vu = 334.56 kN` and a design shear strength of `Vcr = 443.02 kN`, the shear utilisation is 0.755, which is above 0.6, so this is a high-shear case: `beta = (2V/Vd − 1)² = 0.2605` and `Mdv = Md − beta·(Md − Mfd)`.

## Actual Behaviour
| Quantity | As shipped | With the governing `Vd` | 
|---|---|---|
| Vu | 334.56 kN | 334.56 kN |
| Vcr (buckling, governing) | 443.02 kN | 443.02 kN |
| Vd (plastic) used for the trigger | 1989.86 kN | — |
| High-shear threshold `0.6·Vd` | **1193.9 kN** | 265.8 kN |
| `beta_interaction` | **0.0** | 0.2605 |
| M-V Interaction capacity | **7022.18 kNm** | 6052.79 kNm |
| its DCR (Mu = 2235.12 kNm) | 0.3183 | 0.3693 |

The moment capacity used in the M-V check is **13.8 % too high**. The same run reports "ULS Shear Buckling: 334.56 / 443.02, DCR 0.7552" — the program knows the shear utilisation is above 0.6 and still applies no reduction.

A hand check with IS 800 Cl. 9.2.2 gives the same numbers: Mfd (flanges only) = 3300.3 kNm, beta = 0.2605, Mdv = 7022.18 − 0.2605 × (7022.18 − 3300.3) = 6052.8 kNm.

Reproduced in two separate fresh processes. This is not a corner case — of the 20 designs in a routine sweep (spans 20–40 m, carriageway 4.25–7.5 m), **six** had `0.6·Vcr < Vu < 0.6·Vd`, i.e. a missed reduction: carriageway 5.50, 5.75, 6.00, 6.25 and 6.50 m at span 25 m, and the median case above.

## Root Cause
`designer.py:1826` passes `results.Vd_kN` (plastic) rather than the governing design shear strength. `IRC22_2014.cl_603_3_3_3_reduced_bending_under_high_shear` documents its parameter as "Vd_kN # design shear strength" and tests `V_kN <= 0.6 * Vd_kN`, so the wrong value silently disables the whole clause.

## Suggested Fix
```diff
--- a/src/osdagbridge/core/bridge_types/plate_girder/designer.py
+++ b/src/osdagbridge/core/bridge_types/plate_girder/designer.py
@@
-        mv = self.compute_combined_bending_shear(
-            results.Md_kNm, Vu_kN, results.Vd_kN
-        )
+        # Design shear strength governs: web yielding OR web shear buckling
+        # (IS 800 Cl.9.2.2 / IRC 22 Cl.603.3.3.3).
+        Vd_governing = min(results.Vd_kN, results.Vcr_kN) if results.Vcr_kN else results.Vd_kN
+        mv = self.compute_combined_bending_shear(
+            results.Md_kNm, Vu_kN, Vd_governing
+        )
```
A regression test can assert that `beta_interaction > 0` whenever the "ULS Shear Buckling" DCR exceeds 0.6.

## Related Issues
- #234: intermediate stiffener `Fqd` uses the stiffener area; mentions `Vcr` but is a different check.
- #134: lists "M-V Interaction" only among the checks that read zero when the live load is skipped.
