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

(older duplicates / extra-evidence comments to #88, #19, #20, #42, #92 are documented in notes/findings.md)

## Issues already on the repo that our findings duplicate
(duplicate check performed 2026-11-15 against all 39 open+closed issues — see notes/existing_issues.md)
- F1 NaN accepted → #88 (root-cause comment material)
- F2 custom steel density ignored → #20 (also P2-003)
- F4 custom fields wiped after OSI load → #19 (also P2-005)
- CB/end-diaphragm custom grades stored but unused → #43 (P2-002)
- custom deck density not reaching deck load → #41 (P2-004)
- E 350A Gs crash → #42
- missing thermal load case warnings → #92
