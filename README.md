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
- scripts/: fetch_issues, gen_cases, run_headless, case_runner, ui_emulation, analyze, state_runner, make_log_rows, pipeline_probe, smoke_core, osi_sweep (OSI load-time sweep), calc_unit_checks, layout_grid
- tests/: pytest suite (validator limits + .osi round trip)
- report/: LaTeX source and final PDF
- notes/: setup log, code study, findings, run history, existing issues, bug_classes.md, key_flow.csv, osi_load_path.md, web_inventory.md
- PROGRESS.md: checklist

## Issues raised
| # | Title | Link | Status |
|---|-------|------|--------|
| 96 | Loading a .osi file skips all custom-material validation — out-of-range material values load unchallenged | https://github.com/Nidhikhare12/OsdagBridge/issues/96 | open |
| 97 | Toggling input lock can crash when Additional Inputs dialog was never opened (`_additional_inputs_dialog` is None) | https://github.com/Nidhikhare12/OsdagBridge/issues/97 | open (T3 static) |
| 98 | `osdag_core` dependency metadata declares bogus `sqlite` package (breaks clean dependency resolution) | https://github.com/Nidhikhare12/OsdagBridge/issues/98 | open (T5) |
| 99 | `pyproject.toml` runtime dependencies omit required packages and declare unused `pydantic` | https://github.com/Nidhikhare12/OsdagBridge/issues/99 | open (T5) |
| 100 | Inconsistent dependency declarations across `pyproject.toml`, `requirements.txt`, and `environment.yml` | https://github.com/Nidhikhare12/OsdagBridge/issues/100 | open (T6) |
| 101 | README documents CLI usage but installed CLI entrypoint is a stub that ignores arguments | https://github.com/Nidhikhare12/OsdagBridge/issues/101 | open (T6) |
| 127 | `verification_case_01.yaml` and `verification_case_02.yaml` are empty placeholders that fail OSI validation | https://github.com/Nidhikhare12/OsdagBridge/issues/127 | open (T6) |
| 128 | `example_basic.yaml` uses placeholder keys but passes `validate_osi_inputs` vacuously | https://github.com/Nidhikhare12/OsdagBridge/issues/128 | open (T7) |
| 129 | `validate_material_inputs` skips range checks for cross-bracing/end-diaphragm material keys | https://github.com/Nidhikhare12/OsdagBridge/issues/129 | open (T2) |
| 130 | Integer validators raise `OverflowError` on `inf`/`-inf` instead of returning a validation message | https://github.com/Nidhikhare12/OsdagBridge/issues/130 | open (T2) |
| 131 | `saveOSI_inputs` uses `yaml.dump` (unsafe tags) while load uses `yaml.safe_load` — round-trip can fail | https://github.com/Nidhikhare12/OsdagBridge/issues/131 | open (T2) |
| 132 | Skew sign not mirror-symmetric: +15°/−15° give different design demands for a symmetric bridge | https://github.com/Nidhikhare12/OsdagBridge/issues/132 | open (T2) |
| 133 | Valid inputs (span 45 m + median + footpaths) make `design()` run >10 minutes without completing | https://github.com/Nidhikhare12/OsdagBridge/issues/133 | open (T2) |
| 134 | Wrong PASS: silent live-load skip → zero ULS demand (cw 7.5 + median + both footpaths) | https://github.com/Nidhikhare12/OsdagBridge/issues/134 | open (T1) |
| 135 | Second `design()` call on the same object crashes in LTB buckling check (`math domain error`) | https://github.com/Nidhikhare12/OsdagBridge/issues/135 | open (T1) |
| 153 | `saveOSI_inputs` does not enforce the `.osi` file extension (our P6-015, T3 static; filed upstream 2026-11-18) | https://github.com/Nidhikhare12/OsdagBridge/issues/153 | open (T3 → T4 dup of #153) |
| 154 | `loadOSI_inputs` silently swallows exceptions from `solve_extend_basic_input_dict` (our P6-017, T3 static; filed upstream 2026-11-18) | https://github.com/Nidhikhare12/OsdagBridge/issues/154 | open (T3 → T4 dup of #154) |
| 155 | No Web Application Layer — Django Backend and React Frontend absent; web testing blocked (our P1-007, T9; corrected 2026-11-18: stub-only `web/` at repo root) | https://github.com/Nidhikhare12/OsdagBridge/issues/155 | open (T5/T6 → T4 dup of #155) |

## Duplicate-issue comment drafts (extra evidence)
Prepared, evidence-backed comment drafts for existing issues (not new filings). Upstream posting status noted per draft.

| Target issue | Audit ref | Draft | Status |
|---|---|---|---|
| [#43](https://github.com/Nidhikhare12/OsdagBridge/issues/43) CB/end-diaphragm custom grades stored but unused | P2-002 (T4) | [02_comment_43_cb_ed_custom_material_unused.md](notes/issue_drafts/02_comment_43_cb_ed_custom_material_unused.md) | Prepared 2026-11-15; upstream posting pending confirmation |
| [#20](https://github.com/Nidhikhare12/OsdagBridge/issues/20) Custom steel density ignored in `_build_material_props` | P2-003 (T4) | [03_comment_20_custom_girder_density_ignored.md](notes/issue_drafts/03_comment_20_custom_girder_density_ignored.md) | Prepared 2026-11-15; upstream posting pending confirmation |
| [#41](https://github.com/Nidhikhare12/OsdagBridge/issues/41) Custom deck density not reaching `create_deck_load` | P2-004 (T4) | [04_comment_41_custom_deck_density_not_in_load.md](notes/issue_drafts/04_comment_41_custom_deck_density_not_in_load.md) | Prepared 2026-11-15; upstream posting pending confirmation |
| [#19](https://github.com/Nidhikhare12/OsdagBridge/issues/19) OSI load does not restore `_material_custom_fields` | P2-005 (T4) | [05_comment_19_material_custom_fields_not_restored.md](notes/issue_drafts/05_comment_19_material_custom_fields_not_restored.md) | Prepared 2026-11-15; upstream posting pending confirmation |
| [#153](https://github.com/Nidhikhare12/OsdagBridge/issues/153) `saveOSI_inputs` does not enforce `.osi` file extension | P6-015 (T4) | [25_comment_153_osi_extension_t4.md](notes/issue_drafts/25_comment_153_osi_extension_t4.md) | Prepared 2026-11-18; confirms upstream report; reclassified T3→T4 |
| [#154](https://github.com/Nidhikhare12/OsdagBridge/issues/154) `loadOSI_inputs` silently swallows exceptions | P6-017 (T4) | [26_comment_154_osi_swallow_t4.md](notes/issue_drafts/26_comment_154_osi_swallow_t4.md) | Prepared 2026-11-18; confirms upstream report; reclassified T3→T4 |
| [#155](https://github.com/Nidhikhare12/OsdagBridge/issues/155) No Web Application Layer found | P1-007 (T4) | [27_comment_155_web_layer_absent_t4.md](notes/issue_drafts/27_comment_155_web_layer_absent_t4.md) | Prepared 2026-11-18; corrected inventory; reclassified T9→T4 |

(older duplicate notes, e.g. #88/#42/#92 root-cause material, are also documented in `notes/findings.md`.)

## Issues already on the repo that our findings duplicate
(duplicate check refreshed 2026-11-18 against all 92 open+closed issues — see notes/issues_raw.json and notes/STATE.md)
- F1 NaN accepted → #88 (root-cause comment material)
- F2 custom steel density ignored → #20 (also P2-003)
- F4 custom fields wiped after OSI load → #19 (also P2-005)
- CB/end-diaphragm custom grades stored but unused → #43 (P2-002)
- custom deck density not reaching deck load → #41 (P2-004)
- E 350A Gs crash → #42
- missing thermal load case warnings → #92
- `saveOSI_inputs` without `.osi` enforcement → #153 (also P6-015, T3→T4)
- `loadOSI_inputs` silently swallowing solver exceptions → #154 (also P6-017, T3→T4)
- Web application layer absent/stub-only → #155 (also P1-007, T9→T4)


## Additional findings documented (not yet filed upstream)
- **P6-014 (T2)** — `validate_additional_inputs` accepts NaN/inf for ALL 17 keys in `_ADDITIONAL_KEYS` (`typical_section.girder_spacing=nan`, `typical_section.no_of_girders=inf`, ...); root cause `validator.py:174` `_to_float` + always-False NaN comparisons. Draft: `notes/issue_drafts/24_validate_additional_inputs_accepts_nan_inf.md`; evidence `test_cases/os_sweep_results.csv` (9299-case sweep).
- **P6-016 (T3)** — `saveOSI_inputs` overwrites existing files silently, no confirmation dialog (`template_page.py:811-819`).

## Recent updates (2026-11-18)
- Duplicate check refreshed: 155 items, 92 issues (max #155).
- #153 / #154 / #155 were filed upstream 2026-11-18 (matching this session's P6-015 / P6-017 / P1-007); those findings are now T4 duplicates, documented in `report/report.tex`/`report.pdf` and `notes/all_issues_and_bugs.md`.
- W5: bug classes built (`notes/bug_classes.md`), key flow traced (`notes/key_flow.csv`), OSI sweep carried out (`scripts/osi_sweep.py`).
