# Proof — #208: Design log warnings and errors are never written to the PDF report

**Issue:** https://github.com/Nidhikhare12/OsdagBridge/issues/208  
**Severity:** S2 · Medium · **Tier:** T1 confirmed  
**Environment:** OsdagBridge `dev` @ `d74f56d` · macOS 13.6 (Darwin 22.6.0) · conda env `osdagbridge-env` · tested 2026-11-21

## Reproduce
```bash
source ~/miniconda3/etc/profile.d/conda.sh && conda activate osdagbridge-env
cd osdagbridge-testing-report
python proofs/208_design_log_dropped_from_report/scripts/probe_ch8_log.py
python proofs/208_design_log_dropped_from_report/scripts/proof_208_report_e2e.py /tmp/proof208
```

## Expected
INFO/WARNING/ERROR lines passed as `log_entries` appear in the report.

## Actual
`build_report_payload` carries the three marker lines, but the generated `.tex`/PDF contains none of them.

## Evidence in this folder
| File | What it shows |
|---|---|
| `logs/proof_208_report_e2e.log` | End-to-end, two runs: `PAYLOAD log_entries = [...3 markers...]` then `TEX contains MARKER... -> False` for all three |
| `report_output/report_208.tex, report_output/report_208.pdf` | The complete generated report from run 1 (search for MARKER: absent) |
| `logs/probe_ch8_log.log` | Unit level, two processes: `ch8_design_log([...])` output has no marker; chapter title is *Standards & Assumptions* |
| `logs/probe_ch8_fix.log` | Fix proof: appending `lines_tex` to the return value → markers present |

## Root cause
`chap8.py:38` returns only `_ch8_assumptions(is_custom)`; `lines_tex` (lines 11-34) is never used (since commit `b6c0a10`).

## Notes
Markers deliberately contain no `_` because the function escapes underscores. The OsdagBridge clone was never modified; fixes were proven by monkeypatching a copy inside the test scripts. The issue or comment text as drafted is in `ISSUE_208.md`.
