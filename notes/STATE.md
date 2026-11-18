# QA STATE — OsdagBridge (plate girder, branch dev)

## Environment & paths
- Testing repo (write here): `/Users/macbook/Projects/osdagbridge-testing-report`
- OsdagBridge clone (READ-ONLY): `/Users/macbook/Projects/OsdagBridge` (branch `dev`, commit `d74f56d`)
- Conda env: `osdagbridge-env` (Python 3.12.16). `baseline.osi` EXISTS (built in W1 via `scripts/drift_check.py`) — Phases 4/5 possible.

## Current phase
- **W1 (2026-11-18) — setup & case bank complete.** Duplicates refreshed: 146 items, 83 issues (max #146, no new since #140-146). `test_cases/baseline.osi` built headless from `BASIC_INPUT_DICT` + `solve_extend_basic_input_dict` (span 30, cw 7.5, skew 0, no median/footpath, Optimized, 4 girders, 2.1 m spacing). `scripts/tricky_values.py` written; `test_cases/tricky_bank.json` saved with 547 values across 6 categories. **W2 (2026-11-18) — layout solver grid complete.** `scripts/layout_grid.py` ran 23 per-case checks; all PASS with zero violations. Width-sum check corrected for median=Yes (carriageway_width is per-way, so total = 2*cw + 2*cb_w + median_width). Skew angle is correctly allowed negative (range -15..15). `ruff`/`pyflakes` not available in env (T9). **W3 (2026-11-18) — property-based validation tests complete.** `scripts/calc_unit_checks.py` ran 8 property tests (P1-P8) with hypothesis fuzzing; all PASS. All core validators match hand-calculated limits; bool/non-finite rejected; string/number consistency; `OsiInputValidator` vs core validator agreement; OSI round-trip safe. **W4 (2026-11-18) — OSI save/load robustness complete.** `scripts/osi_sweep.py` ran 9299 cases (547 keys × 17 value classes) via `validate_osi_inputs`. New findings: P6-014 (T2), P6-015 (T3), P6-016 (T3), P6-017 (T3). Duplicate: P6-021 (T4, duplicate of draft 15/P4I-001). **W5 (2026-11-18) — Web stub analysis complete.** Web layer absent (no `web/` dir in clone or testing repo); no Django backend, no React frontend, no API endpoints. Web testing STOPPED at GATE 0; recorded T5/T6 findings. Next: close-out.

## GitHub filing status (2026-11-18)
- Issues refreshed: 155 items, 92 issues (max #155).
- #153 = P6-015 (.osi extension) → T4 duplicate.
- #154 = P6-017 (silent swallow) → T4 duplicate; comment draft `notes/issue_drafts/26_comment_154_osi_swallow_t4.md`.
- #155 = web layer absent → T4 duplicate (was T5/T6); no comment draft yet (see `notes/web_inventory.md`).
- Still NEW/unfiled: P6-014 (T2, NaN/inf additional inputs) and P6-016 (T3, overwrite confirmation).

## Tier counts (this audit — cumulative)
| Tier | Count | Items |
|---|---:|---|
| T1 Confirmed bug | 0 | — |
| T2 Likely bug | 1 | P6-014: validate_additional_inputs accepts NaN/inf for all 17 keys in _ADDITIONAL_KEYS (NEW, unfiled) |
| T3 Static finding | 4 | P6-016: no overwrite confirmation (NEW, unfiled); plus 3 prior T3 entries. (P6-015 and P6-017 moved to T4 on 2026-11-18.) |
| T4 Duplicate | 9 | P6-015→#153; P6-017→#154; web-absent→#155; P6-021 (draft 15); plus 5 prior T4 entries |
| T5 Installation/env blocker | 2 | prior entries only (web blocker reclassified to T4/#155) |
| T6 Doc/typo/unit-label/wording | 5 | prior entries only (web doc mismatch reclassified to T4/#155) |
| T7 Oddity, maybe intended | 5 | — |
| T8 Checked and correct | 21 | — |
| T9 Could not test | 3 | — |
| **Total** | **50** | arithmetic sum of the rows above |

## Key files
- `notes/all_issues_and_bugs.md`: all findings with tiers and evidence
- `notes/bug_classes.md`: 8 bug classes grouping 89 issues
- `notes/issue_drafts/`: drafts for T1/T2 items and comment drafts for T4 duplicates
- `notes/issue_drafts/24_validate_additional_inputs_accepts_nan_inf.md`: T2 draft
- `notes/key_flow.csv`: key flow tracing user input → read site → output influence
- `notes/osi_load_path.md`: OSI save/load path analysis (W4)
- `notes/web_inventory.md`: web layer inventory (T5/T6 findings)
- `test_cases/baseline.osi`: built headless (span30/cw7.5/skew0/Optimized, 4 girders)
- `test_cases/os_sweep_results.csv`: 9299 case sweep results
- `test_log.md`: executed/logged cases and issue-filing rows
STATE.md is the source of truth for phase, done/next, and tier counts.
STEP 0: duplicates refreshed into notes/issues_raw.json (152 items, 89 issues, max #152).
STEP 1: bug_classes.md built; key_flow.csv built.
METHOD 1: Variant analysis completed — 4 "custom value ignored / silent default" patterns found and traced.
METHOD 2: Per-key sensitivity matrix — not fully executed (headless design runs needed); see notes below.
METHOD 3: Fix-completeness review — not executed; 15 most recent merged PRs would need diff review.
METHOD 4: Guided GUI session — not executed; notes/manual_gui_hunt.md would be written separately.
CLOSE-OUT: T2/P6-014 drafted in notes/issue_drafts/24_validate_additional_inputs_accepts_nan_inf.md; T3/T5/T6 items recorded in all_issues_and_bugs.md and web_inventory.md; T4 item recorded as duplicate of draft 15.

Evidence/logs location: `evidence/logs/`, `scripts/`, `notes/issue_drafts/`
