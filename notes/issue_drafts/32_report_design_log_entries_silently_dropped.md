# [Bug/Report] Design log entries are collected for the report but never written: `ch8_design_log` discards `log_entries`

**Environment:** macOS 13.6 (Darwin 22.6.0), Python (conda env `osdagbridge-env`), OsdagBridge branch `dev`, commit `d74f56d`.

## Description
`build_report_payload` (`report_generator.py:770-792`) collects the design log for the report. It reads `output_dict['design_log']`, or falls back to `bridge_logger.get_success_log()`, with the comment "Design Log chapter content". The log is passed to `ch8_design_log(payload.log_entries, payload.inputs)` at `report_generator.py:937`.

`ch8_design_log` (`chap8.py:8-38`, docstring "Render Chapter 8 using real log_entries") escapes and colours every INFO, WARNING and ERROR line into `lines_tex`. It then returns only `_ch8_assumptions(is_custom)`, and `lines_tex` is never used. The generated PDF therefore contains no design log, including WARNING and ERROR lines, and gives no indication that the log was dropped.

## Steps to reproduce
```python
from osdagbridge.core.reports import chap8
tex = chap8.ch8_design_log(["INFO: UNIQUEMARKER123", "WARNING: UNIQUEMARKER456"], {})
print("UNIQUEMARKER123" in tex, "UNIQUEMARKER456" in tex)   # -> False False
```
Script: `scripts/probe_ch8_log.py`.

## Expected
The chapter contains the supplied log lines, as the docstring and the payload builder intend. Warnings and errors from the design run should be visible in the report.

## Actual
The returned LaTeX (5928 characters) starts with `\chapter{Standards \& Assumptions}` and contains none of the log lines. Reproduced in two fresh processes (`evidence/logs/probe_ch8_log.log`).

## Root cause
`src/osdagbridge/core/reports/chap8.py:38`: `return _ch8_assumptions(is_custom)`. `lines_tex`, built at lines 11-34, is dead. This was introduced in commit `b6c0a10` ("Report Segregation"). If dropping the log was intentional, the dead code, the docstring and the payload comment should be removed instead.

## Suggested fix
```diff
     mode = str(input_dict.get(KEY_DESIGN_MODE, 'Optimized')).strip().lower()
     is_custom = mode in {'custom', 'customized'}
-    return _ch8_assumptions(is_custom)
+    log_tex = ("\\section{Design Log}\n" + "\n".join(lines_tex) + "\n") if lines_tex else ""
+    return _ch8_assumptions(is_custom) + log_tex
```
With this applied to a copy of the function, both markers appear in the output (`evidence/logs/probe_ch8_fix.log`). The chapter-level placement is a maintainer decision.

## Duplicate check
I searched titles and bodies for ch8, chap8, "design log" and log_entries. The only hits were #119 (unclosed \begingroup in chap7) and #49 (feature PR), and neither covers this.
