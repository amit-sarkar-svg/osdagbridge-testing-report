# Title
[Bug/Analysis] Design live load is taken from static vehicles parked at x = 0, never at the critical position — girder live-load moment underestimated (≈ 14 % lower ULS moment on a 40 m span)

# Description

## Environment
- OS: macOS 13.6 (Darwin 22.6.0)
- Python: conda env `osdagbridge-env`
- Branch: `dev`, commit `d74f56d`

## Description
The live load used for girder design (`1.0 LL`, and through it every ULS/SLS combination containing LL) is selected in `create_governing_ll_load_case()` (`analyser.py:1925`) **only from the static vehicle load cases** (`CaseN …`). The moving-load cases are analysed but not used for this selection.

Every static vehicle is placed with its origin at **x = 0** (the left support):
- `analyser.py:1641` — `x_coord = 0.0  # Assuming vehicles start at the beginning of the bridge (x=0)`
- `analyser.py:1834` — `vehicle.set_global_coord(og.Point(x_coord, 0.0, z_coord))`

So the design never sees a vehicle near mid-span. For short spans the vehicle covers most of the span and the error is small; for longer spans it grows quickly.

**Measured in the model (40 m span, carriageway 7.5 m):** all static vehicle point loads lie in x ∈ [0.6, 20.3] m (2 × Class A) and x ∈ [0.81, 13.75] m (1 × Class 70R). Mid-span is at 20 m.

## Steps to Reproduce
1. Inputs: span 40 m, carriageway 7.5 m, skew 0°, no footpath, no median, Optimized (file `inputs/H_s40_params.json`).
2. Run Design.
3. Inspect `grillage_model.vehicle_load_cases_list` (script `scripts/probe_vehicle_positions.py`) — every vehicle starts at x = 0.

## Expected Behaviour
The design live-load effect is the maximum over vehicle positions along the span (the moving-load cases already traverse from −vehicle length to span + vehicle length, `analyser.py:1908-1910`). Statics: for a fixed vehicle the maximum moment on a simply supported span increases with span.

## Actual Behaviour
**Program, vehicles at x = 0 (current) vs the same model with the static vehicles centred on the span** (only the x offset changed; script `scripts/probe_vehicle_centered_fix.py`):

| 40 m span | Current (x = 0) | Vehicles centred | Change |
|---|---|---|---|
| Governing LL max \|Mz_i\| | 1106.3 kNm | 1527.7 kNm | +38 % |
| LL moment per girder | 775–797 kNm | 1362–1389 kNm | +71–79 % |
| Design moment `mu_applied` | 3553.9 kNm | 4137.7 kNm | +16.4 % |

**Hand calculation** (program's own IRC 6 axle tables, single simply supported line, `scripts/hand_fixed_vehicle.py`): moment with the vehicle fixed at x = 0 divided by the moment at the worst position:

| Span | Class A | Class 70R |
|---|---|---|
| 20 m | 0.89 | 1.00 |
| 25 m | 0.90 | 0.92 |
| 30 m | 0.84 | 0.84 |
| 40 m | 0.71 | 0.71 |

**Metamorphic check:** the summed live-load moment over the interior girders is 2240 kNm (20 m), 3216 kNm (30 m) and **3145 kNm (40 m)** — it decreases from 30 to 40 m, which is impossible for the same vehicles if they were placed at the critical position.

Reproduced twice in separate fresh processes (identical vehicle positions and governing LL).

## Root Cause
`analyser.py:1641` fixes `x_coord = 0.0` for all static vehicles, and `create_governing_ll_load_case()` (`analyser.py:1951`) restricts the search to static cases (`str(lc).lower().startswith("case")`).

## Suggested Fix
Either
- select the governing LL from the moving-load envelope (the moving cases already exist), or
- place each static vehicle at the critical longitudinal position for the span, e.g.

```diff
-        x_coord = 0.0  # Assuming vehicles start at the beginning of the bridge (x=0)
+        # Place the vehicle so its axle group is centred on the span (or search positions
+        # for the maximum moment); x = 0 misses the mid-span maximum on longer spans.
+        x_coord = max(0.0, (self.L - vehicle_length) / 2.0)
```

With the centring applied in a test (monkeypatch), the governing LL and `mu_applied` rise as shown above.

## Impact
Unconservative: the live-load part of every girder demand (ULS flexure/shear, live-load deflection, fatigue stress range) is underestimated, increasingly with span (≈ 10 % at 25 m, 16 % at 30 m, 29 % at 40 m on the vehicle moment).

## Duplicate Check
Searched all 210 issues (open and closed), titles and bodies, for x = 0 / x_coord / vehicle placed / static vehicle / governing LL / mid-span / moving load / `vehicle_lane_coordinates` / `create_governing_ll`. Related but different: #142 (vehicle choices ignored), #140 (impact factor fixed at 0.10), #134 (live load skipped entirely), #87 (seismic reads LL = 0). None reports the longitudinal placement.
