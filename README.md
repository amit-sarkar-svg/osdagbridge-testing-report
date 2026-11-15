# OsdagBridge Testing Report

FOSSEE Winter Internship screening task: testing the short-span steel girder bridge module.

## Environment
- macOS (Intel), Miniconda, env: osdagbridge-env; Python 3.12.16; PySide6 6.11.3 (pip)
- Branch tested: dev (commit: d74f56d, 2026-07-26 "fix: Z,Sa/g,Ah,Av in Report"), read-only — no source edits

## Structure
- test_log.md: every test case with exact inputs and results
- test_cases/: saved .osi input files (baseline + generated/ mutations + manifest.json)
- dictionaries/: per-case Input/Output dictionary dumps + result.json + case.log
- evidence/: tracebacks, probe outputs, screenshots
- scripts/: fetch_issues, gen_cases, run_headless, case_runner, ui_emulation, analyze, state_runner, make_log_rows, pipeline_probe, smoke_core
- tests/: pytest suite (validator limits + .osi round trip)
- report/: LaTeX source and final PDF
- notes/: setup log, code study, findings, run history, existing issues
- PROGRESS.md: checklist

## Issues raised
| # | Title | Link | Status |
|---|-------|------|--------|
| 96 | Loading a .osi file skips all custom-material validation — out-of-range material values load unchallenged | https://github.com/Nidhikhare12/OsdagBridge/issues/96 | open |
| 97 | Toggling input lock can crash when Additional Inputs dialog was never opened (`_additional_inputs_dialog` is None) | https://github.com/Nidhikhare12/OsdagBridge/issues/97 | open (T3 static) |
| 98 | `osdag_core` dependency metadata declares bogus `sqlite` package (breaks clean dependency resolution) | https://github.com/Nidhikhare12/OsdagBridge/issues/98 | open (T5) |

## Duplicate-issue comment drafts (extra evidence)
Prepared, evidence-backed comment drafts for existing issues (not new filings). Upstream posting status noted per draft.

| Target issue | Audit ref | Draft | Status |
|---|---|---|---|
| [#43](https://github.com/Nidhikhare12/OsdagBridge/issues/43) CB/end-diaphragm custom grades stored but unused | P2-002 (T4) | [02_comment_43_cb_ed_custom_material_unused.md](notes/issue_drafts/02_comment_43_cb_ed_custom_material_unused.md) | Prepared 2026-11-15; upstream posting pending confirmation |
| [#20](https://github.com/Nidhikhare12/OsdagBridge/issues/20) Custom steel density ignored in `_build_material_props` | P2-003 (T4) | [03_comment_20_custom_girder_density_ignored.md](notes/issue_drafts/03_comment_20_custom_girder_density_ignored.md) | Prepared 2026-11-15; upstream posting pending confirmation |
| [#41](https://github.com/Nidhikhare12/OsdagBridge/issues/41) Custom deck density not reaching `create_deck_load` | P2-004 (T4) | [04_comment_41_custom_deck_density_not_in_load.md](notes/issue_drafts/04_comment_41_custom_deck_density_not_in_load.md) | Prepared 2026-11-15; upstream posting pending confirmation |
| [#19](https://github.com/Nidhikhare12/OsdagBridge/issues/19) OSI load does not restore `_material_custom_fields` | P2-005 (T4) | [05_comment_19_material_custom_fields_not_restored.md](notes/issue_drafts/05_comment_19_material_custom_fields_not_restored.md) | Prepared 2026-11-15; upstream posting pending confirmation |

(older duplicate notes, e.g. #88/#42/#92 root-cause material, are also documented in `notes/findings.md`.)

## Issues already on the repo that our findings duplicate
(duplicate check performed 2026-11-15 against all 39 open+closed issues — see notes/existing_issues.md)
- F1 NaN accepted → #88 (root-cause comment material)
- F2 custom steel density ignored → #20 (also P2-003)
- F4 custom fields wiped after OSI load → #19 (also P2-005)
- CB/end-diaphragm custom grades stored but unused → #43 (P2-002)
- custom deck density not reaching deck load → #41 (P2-004)
- E 350A Gs crash → #42
- missing thermal load case warnings → #92
