# Extreme-QA BUG REPORT (xrun framework, session X1 — 2026-11-21)

## Counts
| Layer | Cases | Pass | Fail | Timeout | Error | OOM |
|---|---:|---:|---:|---:|---:|---:|
| L2 layout grid | 33 | 33 | 0 | 0 | 0 | 0 |
| L3 .osi loader | 700 | 700 | 0 | 0 | 0 | 0 |
| L1 validators | 1233 | 1233 | 0 | 0 | 0 | 0 |
| **Total** | **1966** | **1966** | **0** | **0** | **0** | **0** |

Tiers: T1 = 0, T2 = 0, T3 = 0, T7 = 0. Layers L4-L7, L5-soak, L8, L9-static: NOT RUN (resume).

## Findings this session (ranked)
**None found yet in L1/L2/L3 (all pass).** Confirmed-stable:
- L2 grid span/cw/skew ±15/footpath/median/mode: solve_extend_basic_input_dict never raises; span/cw stay finite after solve.
- L3 loader: every key × value-bank through yaml.dump→safe_load→validate_osi_inputs: no crash; loader oracle pass.

## Pending (resume, not run this session)
- L4 design pipeline (crash sweep, corners, one-key-at-a-time sensitivity, metamorphic, invariants) — reruns the IDEM2 crash-twice case to confirm #135 via xrun.
- L5 multi-run/state + soak. L6 outputs/report. L7 offscreen Qt. L8 CLI. L9 static.
- Design-twice crash (IDEM2/same.log): expected T1, diff to run again via `scripts/xrun.py --ids <new id>`.

## Stage log
- Stage 1 framework: xrun.py, triage.py, minimize.py, registry.py, run_one.py, case libs L1/L2/L3; `xrun --dry-run` OK; `run_one` patched for RLIMIT_AS (no-op here, machine won't allow: use driver psutil OOM watchdog).
- Stage 2 runs: L2=33 PASS, L3=700 PASS, L1=1233 PASS; triage clusters=1 (all PASS).
- Verify: `python scripts/xrun.py --layers L2,L3 --parallel 3`; rerun `--rerun-failed` smoke.
