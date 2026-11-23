# Title
[Bug/Design] Longitudinal shear VL (Cl.606.4.1) takes A·ȳ about the plastic neutral axis xu but divides by the elastic composite inertia Ic, understating VL by 29 % — deck transverse reinforcement requirement comes out 29 % low

# Description

## Environment
- OS: macOS 13.6 (Darwin 22.6.0)
- Python: conda env `osdagbridge-env`
- Branch: `dev`, commit `d74f56d`

## Description
`IRC22_2014.cl_606_4_1_longitudinal_shear_and_spacing` (`irc22_2015.py:1753-1777`) computes the longitudinal shear flow as:

```python
n     = Es_MPa / Ecm_MPa                 # :1757
t_eff = min(xu_mm, t_slab_mm)            # :1760
Aec   = beff_mm * t_eff / n              # :1763
Y     = xu_mm - (t_eff / 2.0)            # :1766
VL_N_per_mm = V_N * (Aec * Y) / Ic_mm4   # :1776
```

This is the elastic shear-flow formula `VL = V·A·ȳ / I`, which requires `A` and `ȳ` to be taken about the **elastic** neutral axis of the very section whose second moment of area `Ic` is used. Two inconsistencies:

1. **Plastic depth with elastic inertia.** `xu` is the *plastic* neutral-axis depth from the ULS moment calculation (Cl. 603.3.1), while `Ic` is the *elastic* short-term composite inertia (Cl. 604.3), whose neutral axis sits elsewhere. For the case below xu = 207.598 mm but the elastic neutral axis is at 274.748 mm from the top of the slab — a value the program computes and reports itself as `y_top_comp_mm`. Using `Y = xu − t_eff/2 = 103.799 mm` instead of `ȳ = 274.748 − 125 = 149.748 mm` understates the lever arm by a third.
2. **Modular ratio without the code floor.** Line 1757 uses `n = Es/Ecm = 6.061`, while the composite section properties that produced `Ic` use the IRC 22 Cl. 604.3 minimum of 7.5 (`designer.py:1080-1082`, `cl_604_3_modular_ratio`). The transformed slab area is therefore not the one `Ic` belongs to. On its own this defect is conservative; defect 1 outweighs it.

`VL` is used twice: for the ULS stud spacing (`sl1`) and, per the comment at `designer.py:1950-1951`, for the deck transverse-shear check of Cl. 606.10, which sizes the slab transverse reinforcement.

## Steps to Reproduce
1. Inputs: span 20 m, carriageway 7.5 m, skew 0°, no footpath, no median, Optimized.
2. Run Design.
3. Read `design_results`: `VL_N_per_mm`, `xu_mm`, `y_top_comp_mm`, `I_comp_short_mm4`, `Ast_required_cm2_per_m`, `steeldesign.transverse_shear.vl_kN_per_m`.

## Expected Behaviour
With the short-term composite section (n = 7.5, Ic = 11 719 028 660 mm⁴, elastic NA 274.748 mm from the top of the slab, whole 250 mm slab in compression):

- transformed slab area = 2100 × 250 / 7.5 = 70 000 mm²
- ȳ = 274.748 − 125 = 149.748 mm
- VL = 183 500 × 70 000 × 149.748 / 11 719 028 660 = **164.14 N/mm**

(The elastic neutral axis checks out against the program's own value: (70 000 × 125 + 19 584 × 810) / 89 584 = 274.75 mm.)

## Actual Behaviour
| Quantity | As shipped | Elastic NA, n floored at 7.5 | Change |
|---|---|---|---|
| `VL_N_per_mm` | **116.913** | 164.136 | +40.4 % |
| Stud spacing `sl1` (ULS) | 1631.35 mm | 1162.00 mm | −28.8 % |
| Stud spacing governing / provided | 303.81 mm | 303.81 mm | unchanged |
| Deck transverse shear `VL` | 116.913 kN/m | 164.136 kN/m | +40.4 % |
| **`Ast_required_cm2_per_m`** | **0.585** | **0.821** | **+40.4 %** |
| `ur_composite_trans_shear` | 0.117 | 0.1643 | +40.4 % |

So the shipped value is **28.8 % below** the elastic value. The required transverse reinforcement is reported 29 % low. In this case the stud spacing actually provided is unchanged, because the full-shear-connection criterion (303.81 mm) governs over `sl1`, and the provided reinforcement (11.38 cm²/m, set by other minima) is far above either requirement — so no check flips. The reported design quantity is nevertheless wrong, and `sl1` would govern on a girder with higher shear.

Reproduced in two separate fresh processes with identical values.

## Root Cause
`irc22_2015.py:1757` (modular ratio without the Cl. 604.3 floor) and `:1766` (`Y` measured from the plastic neutral axis) combined with the elastic `Ic` at `:1776`.

## Suggested Fix
Compute `A·ȳ` about the elastic neutral axis of the same transformed section that gives `Ic`, with the same modular ratio:

```diff
-        n = Es_MPa / Ecm_MPa
+        n = max(Es_MPa / Ecm_MPa, 7.5)          # IRC 22:2015 Cl.604.3 lower bound
...
-        t_eff = min(xu_mm, t_slab_mm)
-        Aec = beff_mm * t_eff / n
-        Y = xu_mm - (t_eff / 2.0)
+        # Elastic transformed slab area and its lever arm about the ELASTIC neutral
+        # axis of the section that Ic belongs to (pass it in rather than using xu,
+        # which is the plastic depth from Cl.603.3.1).
+        Aec = beff_mm * t_slab_mm / n
+        Y = na_elastic_from_top_mm - t_slab_mm / 2.0
```
`na_elastic_from_top_mm` is already available to the caller as `y_top_comp_mm`. A regression test can assert `VL == V·A·ȳ/I` with A, ȳ and I all taken from the same transformed section.

## Related Issues
- #175: shear connector spacing table reports PASS when the provided spacing exceeds the governing limit — a different defect in the same check.
- #185: deck slab dead-load moment omits the wearing course — also under-states a deck design quantity, by a different route.
