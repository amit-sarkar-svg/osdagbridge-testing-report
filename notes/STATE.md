# QA STATE — OsdagBridge (plate girder, branch dev)

## Environment & paths
- Testing repo (write here): `/Users/macbook/Projects/osdagbridge-testing-report`
- OsdagBridge clone (READ-ONLY): `/Users/macbook/Projects/OsdagBridge` (branch `dev`, commit `d74f56d`)
- Conda env: `osdagbridge-env` (Python 3.12.16). `baseline.osi` **MISSING** (blocks Phases 4,5).

## Current phase
- **Phase 4 (headless design sweep + oracle checks) — completed 2026-11-17.** 25-case pairwise sweep done, 3 wrong-PASS + 3 timeouts + 1 idempotence crash found. Remaining: hand-check statics, Optimized→Custom round-trip, custom-material sensitivity (T8 checks); Phase 4 design() with app-saved `baseline.osi` still blocked.

## What is done
- Phases 0–2 and Phase 3 (prior): issues fetched earlier; UI/core mapping and drift checks done. Issues filed/recorded: #96–#101, #127, #128, #129. Comment drafts #43/#20/#41/#19 prepared.
- **Session 2 (2026-11-17):** refreshed duplicates again → `notes/issues_raw.json` (129 total, 70 issues, 59 PRs, max #129; `evidence/logs/refresh2_summary.txt`). Ran 4 tracks (no baseline/design run):
  - **F (validator fuzz):** `scripts/validator_fuzz.py`, `evidence/logs/trackF_validator_fuzz.{txt,json}` — 5460 calls, 242 flags. **P4F-001 (T2)** `OverflowError` for `inf/-inf` on 5 integer validators (draft `notes/issue_drafts/14_validator_integer_fields_raise_overflowerror_on_inf.md`). **P4F-002 (T4 dup #88)** NaN/inf accepted widely (132). **P4F-003 (T7)** bool accepted as numeric in 100 cases.
  - **G (location/weather):** `scripts/location_fuzz.py`, `evidence/logs/trackG_location_weather.{txt,json}` — 34 cases, 0 exceptions. **P4G-001 (T7)** out-of-range/outside-India coords and unknown zone strings accepted. Read `project_location.py` (~1260–1360) for `get_selected_location`/weather display (no executed GUI dialog test).
  - **H (LaTeX escaping):** no `pylatex/NoEscape/escape_latex`; custom escaping in `core/reports/report_utils.py`, partial in `chap8.py`; pdflatex flow in `report_generator.py`. **P4H-001 (T3)** end-to-end special-char free-text report generation not executed.
  - **I (OSI save/load):** `yaml.dump` vs `yaml.safe_load` incompatibility reproduced — **P4I-001 (T2)** unsafe tags for np.float64/tuple/set break safe_load (`evidence/logs/trackI_yaml_dump_safe_load.txt`, draft `notes/issue_drafts/15_save_osi_yaml_dump_unsafe_tags_break_safe_load.md`). Static read of `template_page.py:793-880` — **P4I-002 (T8/T7 partial)** no in-code extension enforcement, load rejects invalid before populate and catches errors, GUI I/O not executed.

## What is next
- File/record P2-006 (#?) and any chosen drafts (P4F-001, P4I-001, etc.) as directed; post pending comment drafts #43/#20/#41/#19 upstream if desired.
- Finish remaining Track H/G depth if needed: headless report generation with special-char free-text, `get_selected_location` consumption/edge cases (`weather_data`/`display_text` usage grep/read).
- Phase 4 when `baseline.osi` exists: OSI robustness & headless design runs (per-case subprocess, ~10 min timeout, logs in `evidence/logs/`), then Phase 5/6.

## Tier counts (new findings, this audit — cumulative)
| Tier | Count |
|---|---:|
| T1 Confirmed bug | 0 |
| T2 Likely bug | 3 |
| T3 Static finding | 3 |
| T4 Duplicate | 5 |
| T5 Installation/env blocker | 2 |
| T6 Doc/typo/unit-label/wording | 4 |
| T7 Oddity, maybe intended | 5 |
| T8 Checked and correct | 5 |
| T9 Could not test | 3 |
| **Total** | **30** |

(Additions this session: T2 +2 P4F-001,P4I-001; T3 +1 P4H-001; T4 +1 P4F-002/#88; T7 +3 P4F-003,P4G-001,P4I-002-mix; T8 +1 P4I-002-mix/checked aspects.)

## Key facts learned
- Duplicates refreshed 2026-11-17 (session 2): 129 items, 70 issues, 59 PRs, max #129. Always search refreshed `notes/issues_raw.json` via `scripts/search_issues.py`.
- **Track F:** integer validators raise `OverflowError` on `inf/-inf` (5 keys). NaN/inf accepted broadly (dup root cause #88). Bool accepted as numeric in-range in many cases.
- **Track G:** `validate_map_coordinates` is numeric-only (accepts out-of-range/outside-India); `validate_custom_weather_data` accepts unknown/empty zone (not "Select Zone").
- **Track H:** reports use custom escaping (report_utils/chap8) and pdflatex; no executed special-char end-to-end test.
- **Track I:** `saveOSI_inputs` uses `yaml.dump` while `loadOSI_inputs` uses `yaml.safe_load` — unsafe tags (numpy scalar/tuple/set) break round-trip. Load validates and shows errors (no false success) per static read.
- Evidence: `evidence/logs/trackF_*`, `trackG_*`, `trackI_yaml_dump_safe_load.txt`, `refresh2_summary.txt`.

## Evidence/log locations
- `evidence/logs/` (phase1–3, issue latexmk logs, refresh logs, trackF/G/I logs), `scripts/` (drift_check, validator_fuzz, location_fuzz), `notes/issue_drafts/` (01–15).
