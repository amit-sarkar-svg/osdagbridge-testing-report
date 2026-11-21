# Title
[Bug/Design] Cross-bracing design forces are read from the horizontal force Vz, so every gravity load (DL, LL) contributes 0 — bracing is sized for 1–3 kN of seismic/wind only

# Description

## Environment
- OS: macOS 13.6 (Darwin 22.6.0)
- Python: conda env `osdagbridge-env`
- Branch: `dev`, commit `d74f56d`

## Description
`CrossBracingForces` derives the diagonal and chord design forces from the **Vz** component of the transverse grillage members at the bracing stations (`crossbracingforces.py:333`, `comp = "Vz_i" if is_i else "Vz_j"`), then resolves `F_diag = Vz_i / cos α`, `F_chord = Vz_i` (`:345-361`).

In ospgrillage the gravity loads act in **y**. The analyser states this itself: "ospgrillage's p parameter is y-direction only" (`analyser.py:1454`). Vz is the horizontal transverse component. As a result:
- for self-weight, deck, dead load and live load, **Vz = 0** in every bracing member, while the vertical shear Vy in the same members is up to 44 kN (1.0 LL) and 54 kN (BASIC_1);
- the bracing design forces come only from the seismic and wind cases (1.5 EQ (a)/(b), WL Transverse): 0.16–3.23 kN;
- the module's own docstring describes the intended force differently, as "Chord force equals the full **vertical shear**" (`crossbracingforces.py:38`). It also carries an open TODO, "Verify sign convention … Confirm against a known result" (`:106`).

The PDF report states that "Forces are derived from the grillage model under the governing load combination (DL + LL + WL)" (`chap5.py:1405`). The governing cases it prints are all `1.5 EQ` / `WL Transverse`.

## Steps to Reproduce
1. Inputs: span 20 m, carriageway 7.5 m, skew 0°, no footpath, no median, Optimized (all other inputs default).
2. Run Design.
3. Inspect `output_dict["crossbracing_forces_dict"]`, and the transverse member forces at the bracing stations (`result_data["forces"][lc][member]["Vz_i"/"Vy_i"]`).

## Expected Behaviour
The bracing members carry part of the vertical load transfer between adjacent girders under dead and live load, as the module's docstring describes ("full vertical shear"). Gravity load cases must therefore contribute to the design forces. At minimum, the report must not claim DL + LL + WL when only EQ/WL govern.

## Actual Behaviour
| Load case | max \|Vz_i\| (read by design) | max \|Vy_i\| (vertical shear) |
|---|---|---|
| SW | 0.00 kN | 1.39 kN |
| DD | 0.00 kN | 17.16 kN |
| 1.0 DL | 0.00 kN | 18.55 kN |
| 1.0 LL | 0.00 kN | 44.28 kN |
| WL Transverse | 0.35 kN | 0.00 kN |
| BASIC_1 | 0.35 kN | 53.96 kN |

Design forces used: G1-G2 diagonal compression **3.068 kN** (1.5 EQ (b)), G3-G4 diagonal tension 3.226 kN (1.5 EQ (b)). Every member is 40 × 40 × 3 with UR ≤ 0.28.

**Same model with only the component changed to the vertical shear described in the docstring** (monkeypatch of `_read_vz` to return Vy):

| | Current (Vz) | Vertical shear (Vy) |
|---|---|---|
| G1-G2 diagonal compression | 3.068 kN (1.5 EQ (b)) | **60.249 kN** (ACCIDENTAL_1: 1.0DL + 1.0DW + 0.75LL) |
| Section selected for it | 40 × 40 × 3 (capacity 19.39 kN) | 50 × 50 × 6 (capacity 62.28 kN, UR 0.92) |
| G3-G4 diagonal tension | 3.226 kN | 60.249 kN |

The 40 × 40 × 3 strut currently selected (19.39 kN) would be at 3.1 × its capacity under the 60.2 kN force.

Reproduced in three separate fresh processes (identical forces).

## Root Cause
`crossbracingforces.py:326-343` (`_read_vz` reads `Vz_i`/`Vz_j`), used at `:402-403`. The header docstring (`:26-27`) assumes Vz is the members' axial force. For vertical (y) loads that component is zero by construction.

## Suggested Fix
Derive the bracing forces from the vertical shear transferred at the bracing station (Vy), and resolve it with the diagonal's vertical component (statics: vertical component of a diagonal force = F·sin α, with α measured from the horizontal). Keep the horizontal (Vz) contribution from wind and seismic loads, and envelope both:
```python
vy = self._read_component(lc, member, "Vy_i")   # vertical shear (gravity)
vz = self._read_component(lc, member, "Vz_i")   # horizontal (wind / seismic)
F_diag = max(abs(vy) / (n_diag * sin_alpha), abs(vz) / cos_alpha)   # n_diag = diagonals sharing the shear
```
Also correct the report sentence at `chap5.py:1405`, which currently says "DL + LL + WL".

## Related Issues
#43 (bracing custom grade unused; the design dicts hard-code E 250), #169 (cross-bracing capacity blank in the output dock), #109 (take-off uses the diagonal area for chords), #111 (bracing forces depend on whether the Additional Inputs dialog was saved). None of these covers the force component.
