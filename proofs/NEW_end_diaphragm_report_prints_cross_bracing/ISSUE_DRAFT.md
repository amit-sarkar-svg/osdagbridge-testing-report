# Title
[Bug/Report] PDF report's "End Diaphragm Design" chapter reprints the cross-bracing tables (chap5 inserts cb_* content), so it shows PASS results that are not the end diaphragm's — even when no end-diaphragm member was designed

# Description

## Environment
- OS: macOS 13.6 (Darwin 22.6.0)
- Python: conda env `osdagbridge-env`
- Branch: `dev`, commit `d74f56d`

## Description
The design computes end-diaphragm forces and member designs separately from the cross bracing (`_design_end_diaphragm_members`, stored as `output_dict["end_diaphragm_forces_dict"]` and `end_diaphragm_design_results`). The PDF report does not use them. Its "End Diaphragm Design" section is built from the **cross-bracing** table variables:

| Report table | Cross Bracing section | End Diaphragm section |
|---|---|---|
| Connection and Section Properties | `cb_forces_content` (`chap5.py:1420`) | `cb_forces_content` (`chap5.py:1464`) |
| Slenderness Ratio Check | `cb_slenderness_content` (`:1430`) | `cb_slenderness_content` (`:1474`) |
| Capacity Summary | `cb_capacity_content` (`:1440`) | `cb_capacity_content` (`:1485`) |

So the End Diaphragm tables are a row-for-row copy of the Cross Bracing tables in every report.

This matters in two ways:
1. **When the end diaphragms were designed, the report still prints the bracing's numbers.** At skew 10° the end diaphragm's own G1-G2 diagonal compression is **6.684 kN** (1.5 EQ (b)); the report's End Diaphragm table prints **4.664 kN**, the cross-bracing value. The end-diaphragm results exist and are simply not read.
2. **When they were not designed at all, the report still shows PASS.** At skew 0° no end-diaphragm member is designed (that is #257), yet the End Diaphragm tables still show sections, capacities and PASS, because they are a copy of the cross-bracing tables.

The "Overall Design Check Summary" also mirrors the cross-bracing rows as "End Diaphragm — Moment" and "End Diaphragm — Shear" (`chap5.py:1004-1015`). These rows hold axial forces in kN (8.34 kN, 3.60 kN for skew 10°) under "Moment"/"Shear" labels.

## Steps to Reproduce
1. Inputs: span 20 m, carriageway 7.5 m, no footpath, no median, Optimized; skew **0°** (case 1) or **10°** (case 2).
2. Run Design.
3. Compare `output_dict["end_diaphragm_forces_dict"]` / `end_diaphragm_design_results` with the generated report (Design Checks chapter), sections "Cross Bracing Design" and "End Diaphragm Design".

## Expected Behaviour
The End Diaphragm section shows the end diaphragm's own forces, sections and checks. If the end diaphragms were not designed, it says so instead of showing PASS.

## Actual Behaviour
| Case | End-diaphragm design | Report "End Diaphragm" tables |
|---|---|---|
| Skew 0° | forces all `None`, no member designed (`{'G1-G2': [], 'G2-G3': [], 'G3-G4': []}`) | 40 × 40 × 3, demand 3.068 kN, UR 0.280, PASS (cross-bracing values) |
| Skew 10° | G1-G2 diagonal compression 6.684 kN, chord compression 6.088 kN | G1-G2 diagonal 4.664 kN, chord 4.248 kN (cross-bracing values) |

The Cross Bracing and End Diaphragm tables are identical (21 of 21 rows) in all three generated reports: skew 0° twice in fresh processes, and skew 10° once. Screenshots of the two capacity tables side by side are attached.

## Root Cause
- `chap5.py:1464`, `:1474`, `:1485` insert the cross-bracing contents into the End Diaphragm section.
- `chap5.py:1004-1015` mirrors the cross-bracing rows into the summary as "Moment"/"Shear".
- The skew-0° case where nothing is designed is #257 (forces read from `Vz_i` at `plategirderbridge.py:2728`); this issue is about the report not reading `end_diaphragm_design_results` whether or not it is populated.

## Suggested Fix
Build `ed_forces_content`, `ed_slenderness_content` and `ed_capacity_content` from `end_diaphragm_forces_dict` / `end_diaphragm_design_results`, mirroring the cross-bracing builders. When a pair has no design, print "not designed (no force)" instead of PASS. Label the summary rows as axial compression/tension.

## Related Issues
- #72: the same substitution in the desktop Transverse Member Design dialog (`transverse_member_design.py`). This issue is the PDF report, a separate code path (`chap5.py`).
- #257: end diaphragms are never designed at skew 0°. That issue explains why the results are empty; this one is that the report prints cross-bracing values in their place, which it also does at non-zero skew where the results are **not** empty.
- #199: empty end-diaphragm results after reloading an .osi file.
- #215: bracing forces are read from Vz.
