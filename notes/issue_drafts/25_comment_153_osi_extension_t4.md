# Comment draft — issue #153 (P6-015 → T4 duplicate)

**Filing:** <https://github.com/Nidhikhare12/OsdagBridge/issues/153> — "[Bug] saveOSI_inputs Does Not Enforce the .osi File Extension" (open, 2026-11-18)

**Finding type:** T4 (duplicate of #153). Originally recorded as T3 (static) during W5 on 2026-11-18; reclassified once #153 appeared.

**Our static review matched the report exactly:**
- File/lines: `src/osdagbridge/desktop/ui/template_page.py:802-812`
- `QFileDialog.getSaveFileName` filter `"Input Files(*.osi)"` is advisory only; `filePath` is passed unmodified to `open(filePath, 'w')`.
- Confirmed the suggested fix is equivalent to ours (`if not filePath.lower().endswith(".osi"): filePath += ".osi"`).

**Local evidence paths (not committed to OsdagBridge):**
- `notes/osi_load_path.md` — STEP 2 save/load path analysis
- `notes/all_issues_and_bugs.md` — P6-015 entry + GitHub filing status section
- `test_log.md` — rows P6-W5-02 / P6-W5-06

**Notes:** No new issue needed; reclassified T3 → T4 in `notes/STATE.md` on 2026-11-18. The companion finding P6-016 (silent overwrite) is NOT filed upstream — separate draft would be needed if desired.
