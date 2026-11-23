# Title
[Bug/Analysis] Crash barrier, railing and median loads never enter the DL combination (create_sidl_combination is never called), so they are missing from every ULS/SLS combination and from the seismic mass — girder demands under-estimated

# Description

## Environment
- OS: macOS 13.6 (Darwin 22.6.0)
- Python: conda env `osdagbridge-env`
- Branch: `dev`, commit `d74f56d`

## Description
`create_dead_load_combination()` (`analyser.py:1516`) builds the `DL` case from four sub-cases (`_DL_ATTRS`, `analyser.py:1532-1537`):

```python
_DL_ATTRS = [
    "self_weight_load_case",
    "deck_load_case",
    "footpath_load_case",
    "sidl_combination",        # crash barrier + railing + median
]
```

`self.sidl_combination` is only ever assigned inside `create_sidl_combination()` (`analyser.py:1564`, assignment at `:1605`). **That method is never called anywhere in the code base** — `grep -rn "create_sidl_combination" src/` returns only its own definition and its docstring. `add_dead_loads()` (`plategirderbridge.py:1311`) creates the crash barrier, railing and median cases at `:1336-1338` and then calls `create_dead_load_combination()` directly at `:1339`, skipping the SIDL step.

So `getattr(self, "sidl_combination", None)` is always `None` and the superimposed dead loads are silently dropped from `DL`. They are still applied to the grillage as their own load cases, so they appear in the results and in the report, which hides the omission.

Because every combination maps `'dead_load' -> 'dead_load_combination'` (`analyser.py:2319` for ULS and `:2517` for SLS), the crash barrier, railing and median are absent from **every** ULS and SLS combination. The seismic mass uses the same case (`analyser.py:1040`), so they are missing from the seismic weight too.

The designer's own comments state the opposite intent: "DL = SW+DC+DD+SIDL, not DW" (`designer.py:569`, `:2959`).

## Steps to Reproduce
1. Inputs: span 20 m, carriageway 7.5 m, skew 0°, no footpath, no median, Optimized (defaults elsewhere). A crash barrier is always present.
2. Run Design.
3. Compare the resultant of `grillage_model.crash_barrier_load_case` with `grillage_model.dead_load_combination`, and compare the `1.0 DL` girder moment with `SW + DD`.

## Expected Behaviour
The permanent superimposed loads are part of the dead load, so `DL = SW + deck + footpath + SIDL` as `_DL_ATTRS` intends, and they carry the dead-load factor in every combination.

## Actual Behaviour
Span 20 m, carriageway 7.5 m, no footpath, no median:

| Quantity | As shipped | With `create_sidl_combination()` called | Change |
|---|---|---|---|
| `crash_barrier_load_case` resultant | 261.6 kN (applied, but unused) | 261.6 kN | — |
| `sidl_combination` | `None` | 261.6 kN | — |
| `dead_load_combination` resultant | **1160.4 kN** (= 97.9 SW + 1062.5 deck exactly) | **1422.0 kN** | +22.5 % |
| `1.0 DL` moment, girder G1 | 483.348 kNm (= SW 40.568 + DD 442.780 exactly) | 553.025 kNm | +69.677 kNm |
| Design moment `Mu` | 1141.82 kNm | 1211.25 kNm | +6.1 % |
| Design shear `Vu` | 183.50 kN | 193.99 kN | +5.7 % |
| `M_sls` | 1092.87 kNm | 1162.30 kNm | +6.4 % |
| Total deflection | 21.522 mm | 22.959 mm | +6.7 % |
| Max DCR | 2.2086 | 2.3489 | +6.4 % |
| Seismic dead-load mass | 1364.4 kN | 1626.0 kN | +19.2 % |

The crash-barrier moment of 69.677 kNm appears in the results as its own load case, but `1.0 DL − (SW + DD) = 0.000 kNm` exactly, which confirms it never enters `DL`.

With footpath = Both Sides and median = Yes (same span and carriageway), the excluded SIDL is larger — crash barrier 261.6 + railing 58.9 + median 80.0 = **400.5 kN**, with `dead_load_combination` 3133.4 kN instead of 3533.8 kN (+12.8 %). (The girder demands for that particular combination are not usable as evidence because of the separate wrong-PASS defect in #134.)

Reproduced in two separate fresh processes with identical values.

## Root Cause
`create_sidl_combination()` (`analyser.py:1564`) is never called, so `sidl_combination` stays `None` and is skipped by the loop at `analyser.py:1540-1546`. Its own docstring says it must be built first: "The superimposed dead loads (crash barrier, railing, median) enter via the SIDL combination rather than as individual sub-cases, so SIDL must be built first" (`analyser.py:1522-1524`).

## Suggested Fix
```diff
--- a/src/osdagbridge/core/bridge_types/plate_girder/plategirderbridge.py
+++ b/src/osdagbridge/core/bridge_types/plate_girder/plategirderbridge.py
@@ add_dead_loads()
         model.create_crash_barrier_load(barrier_load_kN_per_m=barrier_load_kN_m)
         model.create_railing_load(railing_load_kN_per_m=railing_load_kN_m)
         model.create_median_load()
+        model.create_sidl_combination(partial_safety_factor=1.0)
         model.create_dead_load_combination(partial_safety_factor=1.0)
```
With this one line the values in the right-hand column above are produced. A regression test can assert that `dead_load_combination` resultant equals the sum of its sub-case resultants.

Note that IRC 6 Table 3.1 gives SIDL its own partial safety factor, distinct from structural dead load, so a fuller fix would register SIDL as a separate case in the combination map (`analyser.py:2319`, `:2517`) rather than folding it into `DL`. Either way it must not be dropped.

## Related Issues
- #143: the crash barrier and median **magnitudes** are hard-coded defaults instead of the input values. That issue states the loads "are applied to the grillage as line loads"; this issue is that the applied loads never reach any design combination. Both are needed: #143 fixes the magnitude, this fixes the load path.
- #144: notes that `footpath_load_case` is in `_DL_ATTRS` (and argues it belongs in live load); it does not notice that the `sidl_combination` entry in the same list is always `None`.
- #275: thermal actions omitted from combinations — same class of defect, different load.
