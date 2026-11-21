# Title
[Bug/Report] Cross-bracing report tables contradict themselves: KL/r is not KL ÷ r_min (2306 / 8.0 = 288 > 250 printed as 121.9 PASS) and UR is not Demand ÷ Capacity (0.280 printed for 3.068 / 19.39 = 0.158)

# Description

## Environment
- OS: macOS 13.6 (Darwin 22.6.0)
- Python: conda env `osdagbridge-env`
- Branch: `dev`, commit `d74f56d`

## Description
The generated PDF report, section "Cross Bracing Design" (tables "Connection and Section Properties", "Slenderness Ratio Check (IS 800 Cl. 3.8)" and "Capacity Summary"), prints values that cannot be reproduced from the other numbers on the same page.

1. **Slenderness table.** The column "Eff. Length KL (mm)" is the *geometric* member length (`report_generator.py:617-627`: diagonal length / girder spacing, with "K = 1.0" in the note). The column "KL/r" is the slenderness returned by the member design (`:580-587`), which was computed with a different effective length and radius. With the r_min printed one table earlier (8.0 mm, `chap5.py:721-726`):
   - diagonal: 2306 / 8.0 = **288.3** > 250, printed as **121.9 — PASS**;
   - top chord: 2100 / 8.0 = **262.5** > 250, printed as **111.0 — PASS**.

   The design's own values are KL = 1498.9 mm and KL/r = 121.86 (r = 12.3 mm, not the 8.0 mm r_min).
2. **Capacity summary.** The column "UR" is the member module's `efficiency` (`report_generator.py:575-578`), not Demand ÷ Capacity from the same row:
   - G1-G2 diagonal: demand 3.068, capacity 19.390 → 0.158, printed **0.280**;
   - G1-G2 chord: 2.794 / 22.140 = 0.126, printed **0.260**.

   Other rows agree (G3-G4 diagonal 3.226 / 45.0 = 0.072, printed 0.070).
3. **Nature of the bottom chord.** It is listed as "T" with the compression slenderness 111.0. The tension design for the chord reports a slenderness of 170.73.

## Steps to Reproduce
1. Inputs: span 20 m, carriageway 7.5 m, skew 0°, no footpath, no median, Optimized.
2. Run Design.
3. Generate the report with the "Design Checks" chapter.
4. Open Section 3.3 "Cross Bracing Design" (pages 29–31 of 40 in this run).

## Expected Behaviour
Each table is consistent with its own columns. KL/r = (printed KL) / (printed r), or the table prints the effective length and radius actually used. UR = Demand / Capacity, or the column is labelled as what it is.

## Actual Behaviour
As listed above (screenshots of the two tables are attached). Identical in two separate fresh-process runs.

## Root Cause
- `report_generator.py:617-627` (`get_cb_effective_length` returns the geometric length) is combined with `:580-587` (`get_cb_slenderness` returns the design's KL/r) in `chap5.py:751-760`.
- `chap5.py:788-789` (`capacity`, `ur`) prints `get_cb_efficiency` as "UR" next to the demand and capacity from other sources.

## Suggested Fix
Print the effective length and radius used by the member design (`KEY_EFFECTIVE_LENGTH`, r about the buckling axis) next to its KL/r, or compute KL/r from the printed columns. Compute UR in the report as `demand / capacity` from the same row, or label the module's efficiency separately.

## Related Issues
#151 (per-girder tables repeat the controlling girder's values), #175 (shear connector table PASS with spacing over the limit), #121/#172 (table layout). None of these covers the cross-bracing tables.
