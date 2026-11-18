# Comment draft — issue #154 (P6-017 → T4 duplicate)

**Filing:** <https://github.com/Nidhikhare12/OsdagBridge/issues/154> — "[Bug] loadOSI_inputs Silently Swallows Exceptions from solve_extend_basic_input_dict" (open, 2026-11-18, filed by amit-sarkar-svg)

**Finding type:** T4 (duplicate of #154). Originally recorded as T3 (static) during W5 on 2026-11-18; reclassified once #154 appeared.

**Our static review matched the report exactly:**
- File/lines: `src/osdagbridge/desktop/ui/template_page.py:867-870`
- Code: `try: solve_extend_basic_input_dict(self.input_dict) / self.cad_comp_widget.update_from_osdag_inputs(self.input_dict) / except Exception: pass`
- Execution order confirmed: `validate_osi_inputs(data)` (~847) → `populate_from_dict(data)` (~859) → `set_input_dictionary(...)` (~862-863) → solve inside bare `try/except Exception: pass` (~867-870). UI is populated before the solve step, so a failed solver leaves the dock showing values the design rejected — no error shown, no log.
- Suggested fix mirrors ours: catch the exception and surface it (e.g. `CustomMessageBox` / abort the load) instead of `pass`.

**Local evidence paths (not committed to OsdagBridge):**
- `notes/osi_load_path.md` — STEP 2 save/load path analysis (item 4: exceptions silently swallowed)
- `notes/all_issues_and_bugs.md` — P6-017 entries + GitHub filing status section
- `test_log.md` — rows P6-W5-04 / P6-W5-07

**Notes:** No new issue needed; reclassified T3 → T4 in `notes/STATE.md` on 2026-11-18. The companion findings P6-014 (NaN/inf in `_ADDITIONAL_KEYS`, T2) and P6-016 (silent overwrite, T3) are NOT filed upstream.
