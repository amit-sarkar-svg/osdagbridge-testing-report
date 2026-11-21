# CONTEXT — OsdagBridge QA testing repo (/Users/macbook/Projects/osdagbridge-testing-report)

Testing clone: /Users/macbook/Projects/OsdagBridge (dev @ d74f56d, READ-ONLY). env: osdagbridge-env (py3.12.16).

## Git history (test repo)

860dc49 X1: extreme-QA framework (xrun/triage/minimize/registry/cases L1-L3) + BUG_REPORT + STATE
bb7a179 README: list #153/#154/#155 and W5 findings; refresh duplicate-check info
12da7f7 Report: document #155 (web layer absent); correct web inventory
ca5a09e Report: document #153 and #154 (save/load .osi bugs, T3 filed, now T4 dup)
11a9960 Reclassify P6-017 silent-swallow as duplicate of #154
121a57c Record W5 QA findings; reclassify .osi extension bug as dup of #153
300e96f Update STATE for session 11
9972307 Record session 11 calc checks (T8) and #140 duplicate confirmation
f98a80a Update STATE for session 10
604108e Record report silent-success bug (draft 23) and Track I round-trip pass
8558763 Upgrade report CJK draft with end-to-end success-despite-errors evidence
c4884c6 Update STATE for session 9

## Current phase

- **X1 (2026-11-21) — Extreme-QA framework built & run for L1–L3.**
  Framework: `scripts/xrun.py` (subprocess runner w/ driver-side psutil OOM watchdog + 600s timeout), `tests/extreme/{registry.py, run_one.py, oracles.py, bank.py, cases_l1.py, cases_l2.py, cases_l3.py}`, `scripts/triage.py`, `scripts/minimize.py`. Installed: pytest 9.2.0, hypothesis 6.170.15, psutil, PyYAML (env osdagbridge-env).
  Results: **L2 33 PASS, L3 700 PASS, L1 1233 PASS → 1966/1966, 0 fail.** Triage: 1 cluster (all PASS).
  **L4-L7, L5-soak, L8, L9-static: NOT RUN — RESUME HERE.** Design-twice crash (IDEM2/same.log, #135) confirmed by prior sessions; rerun via xrun.
- Prior sessions (W1–W5, 2026-11-15 to 2026-11-18): SSHD, unit/differential checks (W3), OSI sweep (W4), W5 web stub, README/report updates — done.

## Issues/bugs documented (84 entries in notes/all_issues_and_bugs.md)

- ummary counts
- etailed entries
- P1-001 — `osdag_core` metadata declares bogus `sqlite` dependency (T5)
- P1-002 — `pyproject.toml` runtime dependencies omit required/used packages and include unused `pydantic` (T5)
- P1-003 — Inconsistent dependency declarations across `pyproject.toml`, `requirements.txt`, `environment.yml` (T6)
- P1-004 — README documents CLI commands that the stub CLI ignores (T6)
- P1-005 — `examples/plate_girder/verification_case_01.yaml` and `02` are empty placeholders (T6)
- P1-006 — `example_basic.yaml` uses non-real keys yet passes `validate_osi_inputs` vacuously (T7)
- P1-007 — Web entry point is stubbed; desktop-parity (input dict/defaults/validation) cannot be tested (T4 — duplicate of [#155](https://github.com/Nidhikhare12/OsdagBridge/issues/155))
- P1-008 — `pyproject.toml` declares console entry points for desktop and CLI (T8)
- P1-009 — Core packages import successfully in `osdagbridge-env` (T8)
- P2-001 — `InputDock.toggle_lock` dereferences `_additional_inputs_dialog` without None-guard (T3)
- P2-002 — Cross-bracing/end-diaphragm custom material subkeys written but not consumed by design (T4, dup #43)
- P2-003 — Girder custom density ignored in `_build_material_props` (T4, dup #20)
- P2-004 — Deck custom density not consumed in design load path (T4, dup #41)
- P2-005 — OSI/UI load does not restore `_material_custom_fields` (T4, dup #19)
- P2-006 — UI schema typo: `section.additonal_geometry` (T6)
- P2-007 — Main UI data keys/defaults/dropdowns align with `BASIC_INPUT_DICT` and expected values (T8)
- P2-008 — Offscreen dock instantiation for dict read-back could not be completed (T9)
- hase 3 — Validation rule drift (2026-11-17)
- P3-001 — `validate_material_inputs` has no range-validation branches for cross-bracing/end-diaphragm material keys (T2)
- P3-002 — OSI validator does not police unknown enum values for `structure.type`, `geometry.include_median`, `geometry.footpath` (T7)
- P3-003 — `_ADDITIONAL_KEYS` entries with no numeric bound enforced by `validate_additional_inputs` (T3)
- P3-004 — Basic/median cross-field and basic ranges consistent at core and OSI-load (present values) (T8)
- P3-005 — Lint (ruff/pyflakes) on `src/osdagbridge/core` unavailable in environment (T9)
- racks F–I (validation fuzz, location/weather, LaTeX escaping, OSI file I/O) — 2026-11-17 (session 2)
- P4F-001 — Integer additional-input validators raise `OverflowError` on `inf`/`-inf` instead of a validation message (T2)
- P4F-002 — Non-finite `NaN`/`inf` accepted as valid by many validators (T4, dup/root-cause overlap #88)
- P4F-003 — `bool` values accepted as numeric inputs in multiple validators (T7)
- P4G-001 — Map coordinate validator accepts out-of-range and out-of-India coordinates; weather validator accepts unknown zone strings (T7)
- P4H-001 — LaTeX escaping for free-text report fields not fully verified headlessly (T3)
- P4I-001 — `saveOSI_inputs` uses `yaml.dump` (unsafe tags) incompatible with `yaml.safe_load` on load (T2)
- P4I-002 — OSI save/load static observations (extension handling, overwrite, error paths) (T8/T7 mix, partial)
- P5-006 — Wrong PASS: silent live-load skip → zero ULS demand (median Yes + Both Sides footpath + cw 7.5) (T1)
- P5-005 — `design()` non-termination on valid span-45 + median + footpath inputs (T2)
- hase 4 — headless design harness + oracle/metamorphic (2026-11-17, session 3)
- P5-004 — Skew sign is not mirror-symmetric: +θ vs −θ give different design demands (T2)
- P5-001 — Headless design harness works from defaults (no baseline.osi required) (T8)
- P5-002 — Smoke-case output invariants pass (T8)
- P5-003 — "thermal_load load case not available" warnings at load combinations (T4, dup #92)

## BUG_REPORT.md summary

| Layer | Cases | Pass | Fail | Timeout | Error | OOM |
| L2 layout grid | 33 | 33 | 0 | 0 | 0 | 0 |
| L3 .osi loader | 700 | 700 | 0 | 0 | 0 | 0 |
| L1 validators | 1233 | 1233 | 0 | 0 | 0 | 0 |

## test_log.md: 11 P6 rows

## Extreme-QA framework files

- tests/extreme/registry.py
- tests/extreme/run_one.py
- tests/extreme/oracles.py
- scripts/xrun.py
- scripts/triage.py
- scripts/minimize.py
- tests/extreme/cases_l1.py
- tests/extreme/cases_l2.py
- tests/extreme/cases_l3.py
- evidence/xrun/results.jsonl: 1966 rows
## Uncommitted leftovers (not part of commits)

 M evidence/logs/tex_test/specialchars.log
 M scripts/search_issues.py
?? ResourceFiles/
?? dictionaries/CM_Fy380/
?? dictionaries/CM_Fy450/
?? dictionaries/IDEM/
?? dictionaries/IDEM2/
?? dictionaries/OR_CW150/

