# QA STATE — X3 (2026-11-21, dev@d74f56d)
X7 (2026-11-24): filed as #315 (M-V interaction fed plastic Vd, draft 43) and #316 (longitudinal shear VL, draft 44). Drafts 41/42 filed upstream as #312/#313; proof folders renamed. NOT committed.
X6 (2026-11-24): filed as #312 (S1-candidate SIDL never enters DL combination, draft 41) and #313 (S2 beta_b precedence, draft 42). Draft 40 re-scoped: the skew-0 half is now #257 (filed upstream 2026-11-23); the report-substitution half stands. Upstream now has issues up to #310 - re-screen every lead. NOT committed.
X5 (2026-11-22): NEW S2 report End Diaphragm chapter reprints cross-bracing tables (draft 40, proofs/NEW_end_diaphragm_report_prints_cross_bracing); latent T3 tension-section reporting; ED never designed at skew 0 (root #215). NOT committed.
X4 (2026-11-22, oracles round 2): filed as #215 (S1-candidate bracing forces ignore gravity, draft 38) and #216 (S2 bracing report tables contradict, draft 39); duplicates confirmed: #113, #148, #141/#86, #43. Proof folders proofs/215_*, proofs/216_*.
X3 (sections 1+2): filed 2026-11-22 as #211 (S1 static vehicles at x=0, draft 35), #212 (S2 stale PDF, draft 36), #213 (S2 web buckling > squash load, draft 37); proofs/211_*, 212_*, 213_*. Batch: scripts/batch_design.py test_cases/generated/s12_cases.json dictionaries/s12 (20/20 ok; DE_* invalid: params overwritten). L4 sweep paused at 16/32 (resumable). Committed and pushed to main 2026-11-22 (dictionaries/s12 kept local, 63 MB).

UPDATE 2026-11-21 late: issues #206-#210 filed by user (drafts 30-34). proofs/ folder per issue (README+scripts+logs+screens). report/report.tex restructured v2.0 (sections/ includes; l4 counts via scripts/make_l4_counts.py; compile: cd report && pdflatex -output-directory=build report.tex x2; cp build/report.pdf .). README rewritten (backup notes/README_v1_backup.md).
OPEN: L4 sweep continues (12 ok, 2 inconclusive timeouts c_s20_w23.6_k-15_BothSides_mYes, c_s20_w23.6_k15_None_mYes -> rerun ALONE: delete their lines from l4_corners.jsonl and rerun). L5: rerun `python scripts/l5_state.py ABCA` and ABABA ONLY after L4 finishes (main guard fixed).
Done: Stage 0 (issues refreshed: 124 issues, 80 PRs, my 18 issues), Stage 1 (10 subagent reviews -> notes/candidates.csv), Stage 2 static (notes/static_sweep_x2.md), root cause of #135 proven (notes/issue_drafts/28), NaN validator confirmed (draft 29).
X2b: new T1 drafts 30-34; L4 corner sweep running (scripts/l4_corners.py, resumable, evidence/xrun/l4_corners.jsonl; 11/32 ok so far), L5 running (scripts/l5_state.py ABCA, ABABA -> evidence/xrun/l5_*.json). Oracle: scripts/l4_oracle.py.
PREVIOUSLY NOT RUN: L4 design sweeps, L5 multi-run, L6 report/pdflatex, L7 Qt offscreen, L8 CLI, most "needs test" candidates (C06,C07,C09-C23). Resume with those; use scripts/probe_*.py pattern and xrun.py. Earlier L1-L3: 1966/1966 pass (X1).
No servers started. Clone untouched.
# QA STATE — extreme-QA session X1 (2026-11-21, branch dev @ d74f56d)

## Current phase
- **X1 (2026-11-21) — Extreme-QA framework built & run for L1–L3.**
  Framework: `scripts/xrun.py` (subprocess runner w/ driver-side psutil OOM watchdog + 600s timeout), `tests/extreme/{registry.py, run_one.py, oracles.py, bank.py, cases_l1.py, cases_l2.py, cases_l3.py}`, `scripts/triage.py`, `scripts/minimize.py`. Installed: pytest 9.2.0, hypothesis 6.170.15, psutil, PyYAML (env osdagbridge-env).
  Results: **L2 33 PASS, L3 700 PASS, L1 1233 PASS → 1966/1966, 0 fail.** Triage: 1 cluster (all PASS).
  **L4-L7, L5-soak, L8, L9-static: NOT RUN — RESUME HERE.** Design-twice crash (IDEM2/same.log, #135) confirmed by prior sessions; rerun via xrun.
- Prior sessions (W1–W5, 2026-11-15 to 2026-11-18): SSHD, unit/differential checks (W3), OSI sweep (W4), W5 web stub, README/report updates — done.

## Tier counts (cumulative audit)
| Tier | Count |
|---|---:|
| T1 Confirmed bug | 0 |
| T2 Likely bug | 1 |
| T3 Static finding | 6 |
| T4 Duplicate | 9 |
| T5 Install/Env blocker | 2 |
| T6 Doc/wording | 5 |
| T7 Oddity | 5 |
| T8 Checked & correct | 21 |
| T9 Could not test | 3 |
| **Total** | **37** |

## New this session (X1)
- Expect pending: L4/L5 design pipeline — IDEM2 double-design crash.

## Resume prompt for next session (X2)
```
Continue extreme QA (W-audit) — read ONLY notes/STATE.md, then resume. Testing repo: /Users/macbook/Projects/osdagbridge-testing-report. Clone (READ-ONLY): /Users/macbook/Projects/OsdagBridge (dev @ d74f56d). Env: source ~/miniconda3/etc/profile.d/conda.sh && conda activate osdagbridge-env. Budget ~40k (stop ~35k). Never read long files whole (grep -n, sed ≤80 lines); cap output with head -40. Logs: evidence/logs/. Base: test_cases/baseline.osi.

RUN: L4 design pipeline crash sweep (reuse xrun: `python scripts/xrun.py --layers L4 --parallel 1`; wrapper + oracles to add in tests/extreme/cases_l4.py):
- corners: span{20,45}/cw{4.25,23.6}/skew{-15,15}/footpath{None,Both}/median{No,Yes} × Optimized,Custom; run each corner twice back-to-back; first run crash → expect the IDEM2 #135 crash (secondary confirmation).
- 2nd design() on same object for baseline case → expect crash (reproduce twice).
- near-limit: solve_extend_basic_input_dict + design at span 45−1e-9 vs 45: outputs must match within tolerance.
ORACLE L4: design() completes OR raises with a logged meaningful exception; no NaN/inf in output; ratios ∈ [0,1.1]; no negative dims; optimized-then-custom match.

RUN: L5 multi-run/state: A,B,C,A and A,B,A,B,A sequences on one object; design-twice; Optimized→Custom→Optimized; run5==run1. Soak 30 × smallest design, record psutil RSS at 10 checkpoints.

RUN: L7 offscreen Qt UI: QT_QPA_PLATFORM=offscreen, instantiate input dock; traceback watch; 300-step seeded random action sequence; Design with empty required field; double-press Design.

If design() fails to start after 3 attempts, record T9, run L8 CLI checks.

DELIVERABLES: update notes/BUG_REPORT.md (counts, per-tier, per-layer, findings, dup-checks, evidence paths, root causes, suggested fixes as diffs, expected vs actual), notes/issue_drafts/NN_title.md for each T1/T2, comment drafts for T4, notes/manual_gui_checklist.md, test_log.md rows, notes/STATE.md, commit+push to https://github.com/amit-sarkar-svg/osdagbridge-testing-report.
END: counts per tier and layer, top findings one-liners (severity/confidence), what I could not test, resume prompt, STOP.
```

## Servers started
- None (framework-only session; no app servers).

## Servers to stop before finish
- N/A.
