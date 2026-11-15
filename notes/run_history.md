# Run History (honest record of what was executed)

## 2026-11-15
- `scripts/fetch_issues.py` — OK. 95 items page 1 (56 PRs skipped) → 39 issues → notes/issues_raw.json, notes/existing_issues.md.
- `scripts/smoke_core.py` — OK. Imports + validator boundary calls headless (see file).
- `python -m pytest tests/ -q` → 18 passed, 1 failed (PYT-04 NaN span, intentional detector), 1 skipped (baseline round-trip, waits for baseline).
- `scripts/pipeline_probe.py` (run 1, no priming) — design_error at Stage 5: "Gs not set for grade 'E 350A'" (designer.py L311). Probe artifact: UI primes material.girder.g before design; probe did not. NOT a new bug; related existing issue #42 to be re-checked.
- `scripts/pipeline_probe.py` (run 2, with ui_emulation priming, QT_QPA_PLATFORM=offscreen) — design_ok in 60.5 s. Full design pipeline confirmed to work headless; per-case timeout sized at 600 s.
- Note: macOS `timeout` command unavailable; subprocess timeouts implemented in run_headless.py instead.
