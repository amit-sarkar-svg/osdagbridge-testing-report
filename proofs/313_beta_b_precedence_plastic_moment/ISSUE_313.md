# Title
[Bug/Design] Operator precedence in cl_8_2_1_2_design_bending_strength makes beta_b always 1.0, so Semi-Compact and Slender girders are given the full plastic moment — LTB resistance overstated by Zp/Ze (12.3 % on a 20 m plate girder)

# Description

## Environment
- OS: macOS 13.6 (Darwin 22.6.0)
- Python: conda env `osdagbridge-env`
- Branch: `dev`, commit `d74f56d`

## Description
The design bending strength of IS 800:2007 Cl. 8.2.1.2 is computed as:

```python
beta_b = 1.0 if section_class == KEY_Plastic or KEY_Compact else Ze/Zp
```

Python parses this as `(section_class == KEY_Plastic) or KEY_Compact`. `KEY_Compact` is the non-empty string `"Compact"`, which is always truthy, so **the condition is true for every section class** and `beta_b` is always `1.0`. The `Ze/Zp` branch is unreachable.

The line is present in two copies:
- `osdagbridge/core/utils/codes/is800_2007.py:1026` (bundled fallback copy);
- `osdag_core/utils/common/is800_2007.py:1012` in the `osdag_core` dependency — **this is the copy actually executed**, because `irc22_2015.py:9-11` imports `IS800_2007` from `osdag_core` first and only falls back to the bundled copy.

The value flows straight into the girder LTB check. `IRC22_2014.cl_603_3_3_1_buckling_resistance_moment` (`irc22_2015.py:609`) takes `Mpl` from that function and returns `Mpl_buck = chi_LT * Mpl` (`:649`). IRC22 does compute a correct `beta_b` of its own at `:626-628`, but uses it only for `lambda_LT` (`:639`) — never for the returned moment. So the reduction for Semi-Compact and Slender sections is lost.

A second defect sits in the same path: `designer.py:1008` passes `section_class=section_class.lower()`, so the string reaching the comparison is `"slender"` / `"semi-compact"`, which could never match the capitalised `KEY_Plastic` / `KEY_Compact` constants anyway. Fixing only the precedence would therefore make every section Semi-Compact; both need correcting together.

Plate girder webs are routinely Class 4, so this affects the common case: the program classified the tested 20 m girder as **Slender** (d/tw = 136.0 against a semi-compact limit of 106.49) and still applied the plastic modulus.

## Steps to Reproduce
Unit level:
```python
from osdag_core.utils.common.is800_2007 import IS800_2007
Zp, Ze, fy, gm0 = 8373248.0, 7453608.0, 350.0, 1.1
for sc in ("Plastic", "Compact", "Semi-Compact", "Slender", "slender"):
    print(sc, IS800_2007.cl_8_2_1_2_design_bending_strength(sc, Zp, Ze, fy, gm0, "Simply Supported") / 1e6)
```
Design level: span 20 m, carriageway 7.5 m, skew 0°, no footpath, no median, Optimized → Design → Design Checks → "LTB (Girder SW Only)" and "LTB (Construction Stage)".

## Expected Behaviour
IS 800:2007 Cl. 8.2.1.2: `beta_b = 1.0` for Plastic and Compact sections, `beta_b = Ze/Zp` for Semi-Compact. A Class 4 (Slender) section cannot reach the plastic moment at all and needs effective-section properties; at the very least it must not be given `beta_b = 1.0`.

## Actual Behaviour
Every section class returns the same design bending strength:

| `section_class` passed | Md returned |
|---|---|
| Plastic | 2664.22 kNm |
| Compact | 2664.22 kNm |
| Semi-Compact | 2664.22 kNm |
| Slender | 2664.22 kNm |
| slender | 2664.22 kNm |

Correct value for the tested girder (Ze/Zp = 7453608 / 8373248 = 0.8902): 2371.60 kNm. The cap at `1.2·Ze·fy/γm0` = 2845.92 kNm does not bind, so nothing limits the error.

End to end, span 20 m (the section is classified Slender by the program itself):

| Quantity | As shipped | With the precedence corrected | Change |
|---|---|---|---|
| Implied Mpl (= Mb / χLT) | 2663.85 kNm | 2371.28 kNm | −11.0 % |
| "LTB (Girder SW Only)" capacity | 304.75 kNm | 271.27 kNm | −11.0 % |
| its DCR | 0.1330 | 0.1494 | +12.3 % |
| "LTB (Construction Stage)" capacity | 2316.41 kNm | 2062.00 kNm | −11.0 % |
| its DCR | 0.2085 | 0.2343 | +12.3 % |

The capacity is overstated by exactly Zp/Ze = 1.1234, i.e. **12.3 %**, for every Semi-Compact or Slender girder. In this particular case both LTB checks pass either way, so the verdict does not change; a design whose LTB utilisation lies between 0.89 and 1.00 would be reported as PASS when it fails. Reproduced in two separate fresh processes.

A side effect worth noting: because `beta_b` is constant, the section classification that the program computes and prints (`section_class_governing`) has no influence whatever on the bending resistance.

## Root Cause
`osdag_core/utils/common/is800_2007.py:1012` (executed) and `osdagbridge/core/utils/codes/is800_2007.py:1026` (bundled copy): missing parentheses in the conditional expression. `irc22_2015.py:649` then multiplies `chi_LT` by this unreduced `Mpl`.

## Suggested Fix
```diff
-        beta_b = 1.0 if section_class == KEY_Plastic or KEY_Compact else Ze/Zp
+        sc = str(section_class).strip().lower()
+        if sc in ("plastic", "compact"):
+            beta_b = 1.0
+        elif sc in ("semi-compact", "slender"):
+            beta_b = Ze / Zp          # Slender also needs effective-section properties
+        else:
+            raise ValueError(f"Unrecognised section_class {section_class!r}")
```
(The lower-casing also fixes the case mismatch introduced by `designer.py:1008`.) Since the executed copy lives in `osdag_core`, OsdagBridge should either pin a corrected `osdag_core` or stop preferring it over its own copy at `irc22_2015.py:9-11` — and `irc22_2015.py:649` should apply the `beta_b` it already computes at `:626-628`.

## Related Issues
- #176: case-sensitive `section_type == 'Rolled'` in the same family of functions, which downgrades rolled sections to welded (αLT). Same kind of defect, different variable; neither covers the other.
- #117: nominal yield strength used for every plate thickness — also overstates girder capacity, independently.
