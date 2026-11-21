# Progress Checklist

## Setup
- [x] Fork, clone, dev branch
- [x] Conda env and app launches (workarounds in notes/setup_log.md)
- [x] Env check: `import osdagbridge, osdag_core` OK (headless smoke OK, scripts/smoke_core.py)
- [x] Duplicate check: scripts/fetch_issues.py → notes/issues_raw.json + notes/existing_issues.md (39 issues, no PRs)

## Step 0: Code study
- [x] plategirderbridge.py, defaults.py, validator.py, osi_validator.py, common.py
- [x] template_page.py (Design/Save/Load flow), input_dock.py + material_properties.py (Custom material keys)
- [x] Limits verified vs source → notes/step0_code_study.md
- [x] Baseline check: test_cases/baseline.osi MISSING → asked user → user saves from GUI (blocker for gen_cases/run)
- [ ] Baseline received

## Step 1: Build
- [x] scripts/gen_cases.py (ready; waits for baseline)
- [x] scripts/case_runner.py + scripts/run_headless.py + scripts/ui_emulation.py (ready)
- [x] scripts/state_runner.py, scripts/analyze.py, scripts/make_log_rows.py (ready)
- [x] scripts/pipeline_probe.py — run 1: design_error (missing priming, probe artifact); run 2 with priming: in progress
- [x] pytest tests/ — 18 passed, 1 failed (NaN detector PYT-04), 1 skipped (waits for baseline)
- [ ] test_cases/generated/*.osi + manifest.json (blocked on baseline)
- [ ] dry-run 3 cases → full sequential run
- [ ] analyze + state check + log rows

## Step 2: Report
- [ ] notes/findings.md (candidate bugs w/ evidence + duplicate check)
- [ ] PASS/FAIL table + manual GUI checklist

## Currently waiting on
- User: save baseline from GUI (project location filled, defaults) → test_cases/baseline.osi

## Honest status
- Nothing has been "run" yet for design cases; only import/validator smoke tests executed (see scripts/smoke_core.py output in notes).

## Sessionized audit
- [x] Phase 0 complete (2026-11-15): issues fetched (40), existing_issues.md compacted, STATE.md + all_issues_and_bugs.md created. Baseline missing.


## 2026-11-21 (v2.0)
- [x] Whole-codebase review (10 areas), static sweep (bandit/ruff/pip-audit)
- [x] #135 root cause found and fix proven
- [x] Filed #206, #207, #208, #209, #210 (all T1)
- [x] proofs/ folder per issue; report restructured (v2.0); README rewritten
- [ ] L4 corner sweep completion; rerun 2 inconclusive timeouts alone
- [ ] L5 multi-run sequences (harness fixed)
