# RULES (master prompt summary)

- **Session budget:** keep each session < ~100k tokens. One phase per session. After each sub-step update `notes/STATE.md`. If ~80k, finish sub-step, update STATE, STOP: "Phase X paused at step Y. Start a new session with the resume prompt." When phase completes: "Phase X complete. Start a new session for Phase Y."
- **State in files:** `notes/STATE.md`, `notes/all_issues_and_bugs.md`. A new session continues from STATE.md alone.
- **Reading:** never read large files whole. `grep -n` to locate, then `sed -n 'A,Bp'` (≤150 lines). `plategirderbridge.py` (>3000) and `validator.py` (>1000): never cat.
- **Output:** cap with `head/tail` (e.g. -60). Redirect full logs to `evidence/logs/`; report counts/first error/last ~20 lines. Do not paste long files/tracebacks (quote 3–10 relevant lines). Prefer scripts that print compact summaries.
- **No big sub-agents:** summaries < 200 words only.
- **Mandate:** mention ALL issues/bugs in `notes/all_issues_and_bugs.md` with ID and exactly one tier T1–T9 (T1 confirmed/reproduced twice; T2 likely; T3 static w/ quote; T4 duplicate w/ issue #; T5 env/install blocker; T6 doc/typo/unit/wording; T7 oddity; T8 checked-correct; T9 could not test). Never inflate, never invent evidence. Counts in STATE must match entries.
- **Hard rules:** never modify OsdagBridge source; every claim evidenced (input/output/trace/diff/screenshot/path or quoted file:line); do not post to GitHub (drafts in `notes/issue_drafts/`); log every case incl. passes in `test_log.md`; run executable cases in subprocess w/ 10-min timeout, one log/case; duplicate-check against `notes/existing_issues.md` (+raw) by keyword/file before labeling new. #96 excluded from new.
