# [Bug/Analysis] Skew sign is not mirror-symmetric: +15° and −15° give different design demands for a symmetric bridge

**Filed:** [Nidhikhare12/OsdagBridge#132](https://github.com/Nidhikhare12/OsdagBridge/issues/132) — open (filed 2026-11-17)

**Environment**
- OsdagBridge `dev` @ `d74f56d` (2026-07-26)
- macOS (Intel), conda env `osdagbridge-env`, Python 3.12.16
- Headless design via `PlateGirderBridge().set_input(d); design()` from `BASIC_INPUT_DICT` + `solve_extend_basic_input_dict` (no GUI, no baseline.osi)
- Finding type: **T2 (likely analysis bug — sign-dependent results)**

**Scenario — what we filled (exact inputs)**
Two runs, identical in every field except the sign of the skew angle:

| Field | Value (both runs) |
|---|---|
| structure.type | Highway Bridge |
| geometry.span | 30.0 m |
| geometry.carriageway_width | 10.5 m |
| geometry.include_median | No |
| geometry.footpath | None |
| geometry.design_mode | Optimized |
| materials | defaults (E 350A girder/CB/ED, M40 deck) |
| geometry.skew_angle | **+15.0°** (run A) / **−15.0°** (run B) |

All remaining inputs came from the app's own default flow (`BASIC_INPUT_DICT` → `solve_extend_basic_input_dict` → material priming); no value was invented. The bridge cross-section is symmetric (no median, no footpath), so +15° and −15° are mirror images of each other.

A second, independent pair used the same inputs with skew **+7.5°** vs **−7.5°**.

**What we got (executed output, `dictionaries/OR_SKEW15`, `OR_SKEWM15`, `OR_SKEW75`, `OR_SKEWM75`)**

| Quantity | +15° | −15° | +7.5° | −7.5° |
|---|---|---|---|---|
| `steeldesign.details.moment.mu_applied` (kNm) | 2602.12 | 2376.38 | 2582.22 | 2488.43 |
| `util.shear` (%) | 59.28 | 41.08 | 62.32 | 42.18 |
| `util.fatigue` (%) | 183.74 | 167.06 | 182.25 | 175.33 |
| `util.flexure` (%) | 22.67 | 20.71 | 22.50 | 21.68 |
| `util.deflection_crack` (%) | 55.06 | 49.13 | — | — |

For reference, quantities that depend only on self-weight are **identical** across signs: `util.long_trans_shear = 21.52` in both ±15° runs; `Int.Stiff: Leg ≤ H_limit = 1.479` in both. So the geometry/section itself is mirrored correctly — the divergence appears in load-driven checks (shear, fatigue, deflection, flexure).

**Expected vs actual (the mistake)**
- **Expected:** for a symmetric cross-section, flipping the skew sign mirrors the structure. Every demand/utilisation magnitude should be the same (the controlling girder moves from one edge to the other, but the maximum over all girders is unchanged). A ±15° pair should differ by ~0%, not by 9–44%.
- **Actual:** the positive-skew runs are consistently and substantially higher — `util.shear` is **59.3 vs 41.1** (+15°) and **62.3 vs 42.2** (+7.5°), i.e. ~44–48% higher; design moment differs by ~9%. This means the analysis result depends on the *sign* of a symmetric geometric parameter, which is not physical.

**Why this matters:** a user entering +15° instead of −15° (same physical bridge, mirrored) gets a materially different design — different governing shear/fatigue utilisations and potentially a different PASS/FAIL verdict. It indicates the load application or grillage response is not mirrored with the geometry.

**Logs and proof**
- `scripts/oracle_runs.py` (cases `OR_SKEW15`, `OR_SKEWM15`, `OR_SKEW75`, `OR_SKEWM75`), `scripts/design_runner.py`
- `dictionaries/OR_SKEW15/output.json`, `dictionaries/OR_SKEWM15/output.json`, `dictionaries/OR_SKEW75/output.json`, `dictionaries/OR_SKEWM75/output.json`
- DCR tables parsed from `dictionaries/OR_SKEW15/case.log` etc.; `evidence/logs/oracle_runs1.log`, `evidence/logs/oracle_runs2.log`

**Likely area (root cause not yet pinned to a line)**
`src/osdagbridge/core/bridge_types/plate_girder/analyser.py` builds the grillage with `create_grillage(..., skew=self.angle, mesh_type="Oblique")` (≈L275) and applies loads through `LoadPlacementManager` (`load_placement.py`: deck/footpath/median line & patch loads defined in local x–z coordinates). If moving-vehicle placement or the oblique mesh is not mirrored when the skew sign flips, the positive sign will systematically attract more load. This is the area to inspect; the exact line is still being traced.

**Suggested fix (direction)**
Ensure live-load placement and oblique-mesh node/load mapping are mirror-invariant: when `skew → −skew`, the set of applied vehicle/patch loads and their distribution among girders should be the mirror image, giving identical maximum demands. Add a regression test asserting that DCR magnitudes for +θ and −θ match within tolerance for a symmetric section.

**Duplicate check**
Searched open+closed issues (full titles/bodies, refreshed `notes/issues_raw.json`, 131 items) via `scripts/search_issues.py` for `skew`, `mirror`, `asymmetric` — closest are #89 (skewed bridges retain only one per-girder result) and #124 (inconsistent overall width), neither of which compares +θ vs −θ sign. **No duplicate found.**

**Notes**
Reported as T2 (likely) because the expectation is well-justified by symmetry but the exact responsible line is still under investigation. Confirmed reproducible in two independent sign pairs.
