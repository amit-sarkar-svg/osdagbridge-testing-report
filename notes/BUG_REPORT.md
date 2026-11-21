# Extreme-QA BUG REPORT (xrun framework, session X1 — 2026-11-21)

## Counts
| Layer | Cases | Pass | Fail | Timeout | Error | OOM |
|---|---:|---:|---:|---:|---:|---:|
| L2 layout grid | 33 | 33 | 0 | 0 | 0 | 0 |
| L3 .osi loader | 700 | 700 | 0 | 0 | 0 | 0 |
| L1 validators | 1233 | 1233 | 0 | 0 | 0 | 0 |
| **Total** | **1966** | **1966** | **0** | **0** | **0** | **0** |

Tiers: T1 = 0, T2 = 0, T3 = 0, T7 = 0. Layers L4-L7, L5-soak, L8, L9-static: NOT RUN (resume).

## Findings this session (ranked)
**None found yet in L1/L2/L3 (all pass).** Confirmed-stable:
- L2 grid span/cw/skew ±15/footpath/median/mode: solve_extend_basic_input_dict never raises; span/cw stay finite after solve.
- L3 loader: every key × value-bank through yaml.dump→safe_load→validate_osi_inputs: no crash; loader oracle pass.

## Pending (resume, not run this session)
- L4 design pipeline (crash sweep, corners, one-key-at-a-time sensitivity, metamorphic, invariants) — reruns the IDEM2 crash-twice case to confirm #135 via xrun.
- L5 multi-run/state + soak. L6 outputs/report. L7 offscreen Qt. L8 CLI. L9 static.
- Design-twice crash (IDEM2/same.log): expected T1, diff to run again via `scripts/xrun.py --ids <new id>`.

## Stage log
- Stage 1 framework: xrun.py, triage.py, minimize.py, registry.py, run_one.py, case libs L1/L2/L3; `xrun --dry-run` OK; `run_one` patched for RLIMIT_AS (no-op here, machine won't allow: use driver psutil OOM watchdog).
- Stage 2 runs: L2=33 PASS, L3=700 PASS, L1=1233 PASS; triage clusters=1 (all PASS).
- Verify: `python scripts/xrun.py --layers L2,L3 --parallel 3`; rerun `--rerun-failed` smoke.

---
# X2 session addendum (2026-11-21, dev@d74f56d)
Counts this session: T1 0 new (see below); T4 with new evidence 2; T2 2 (C05, C08); T3 static sweep; layers L4–L8 NOT run in this session.
## Key finding (comment on existing #135, T4 + root cause, confidence high)
`design()` converts girder dims mm->m **in place** every call (plategirderbridge.py:536-589, called at :683). Second `design()` on same object w/o `set_input` re-divides: depth 1.67 -> 0.00167, LTB `math domain error`.
- Input: test_cases/generated/A1_params.json; repro: scripts/probe_double_convert.py (2 fresh processes, logs evidence/logs/probe_double_convert_{1,2}.log).
- Fix proven by monkeypatch (pristine copy per design): run1 == run2 == 1.67, no crash (scripts/probe_double_convert_fix.py).
- Desktop path (template_page.py:689-690 set_input before design) did NOT crash in 2 presses for this input (scripts/probe_ui_path_alias.py) -> severity S2/API-contract, not S1.
- Draft: notes/issue_drafts/28_comment_135_root_cause_double_mm_to_m.md
## T4 comments with new triggers
- #88: validate_basic_inputs / validate_material_inputs accept NaN; bool True accepted as skew (validator.py:1094-1097). Draft 29. Also validate_map_coordinates accepts 999/nan/inf (#180).
## T2
- C05 validator.py:46 `if median` truthy for "No" -> min width 7.5 instead of 4.25 when width None (probe_cands1.log). No existing issue found. Severity S3.
- C08 defaults.solve_extend_basic_input_dict TypeError when carriageway None (defaults.py:908): raised in my own harness; UI likely never passes None -> T2/S3.
## Candidates: notes/candidates.csv (25 rows; most "needs test"). Static sweep: notes/static_sweep_x2.md.

## X2 continued (2026-11-21): NEW findings, not in any existing issue (T1 = reproduced in 2 fresh processes + fix proven on a copy)
| ID | Sev | Title | Draft | Evidence |
|---|---|---|---|---|
| X2-N1 | S2 | Clearing Skew Angle sets skew to -15° (validator.py:63-64; SKEW_ANGLE_DEFAULT=0.0 unused) | 30 | evidence/logs/l7_empty_field.log, l7_empty_skew_fix.log |
| X2-N2 | S2 | Carriageway validator treats Median "No" as median -> 7.5 m min (validator.py:46) | 31 | evidence/logs/probe_median_fix.log |
| X2-N3 | S2 | Design log entries dropped from report: ch8_design_log ignores lines_tex (chap8.py:38) | 32 | evidence/logs/probe_ch8_log.log, probe_ch8_fix.log |
| X2-N4 | S3 | _lookup_material returns None / IndexError (plategirderbridge.py:1124-1167) | 33 | evidence/logs/probe_cands3*.log |
| X2-N5 | S3 | _tex double-escapes backslash -> "\{}" (report_utils.py:18-23) | 34 | evidence/logs/probe_tex_escape.log |
Comments on existing: #135 root cause (draft 28), #88 extra triggers (draft 29).
Checked & correct (T8): pdflatex invoked w/o shell, \input injection escaped (l6 latex_input); CJK project name compiled at d74f56d (l6 stale_cjk); typing nan/inf in dock blocked by QDoubleValidator (l7_ui_probe.log); UI path set_input+design twice OK.
T7: user spacing/overhang always re-derived from girder count (defaults.py:919,932); median carriageway counted twice in overall width (8 m + median -> 18.1 m) — depends on meaning of carriageway_width; "3.0" girder count string -> ValueError.
L8 CLI: stub, rc 0 for every argument incl. missing file (T4 #101). L6 stem "&foo"/"-foo": pdf_path None reported honestly (T8). One run with stem "-foo" stalled >600 s while 2 later reruns finished in <90 s: not reproducible, T7 (no subprocess timeout, report_generator.py:969).
