# Title
[Bug/Report] generate_report returns an older PDF as the new report when compilation fails (success is judged only by "a file with that name exists")

# Description

## Environment
- OS: macOS 13.6 (Darwin 22.6.0)
- Python: conda env `osdagbridge-env`
- Branch: `dev`, commit `d74f56d`

## Description
`generate_report()` decides success with `if os.path.exists(pdf_path)` on the **output folder** (`report_generator.py:981-983`). The freshly compiled PDF is copied back only if it exists in the temporary folder (`:978-979`). If compilation fails, a PDF left in the output folder by an earlier report is returned as `ReportResult(pdf_path=...)`, i.e. reported as a successful new report. The `.tex` next to it is the new one, so the folder ends up with a `.tex` and a `.pdf` that describe different projects/designs.

## Steps to Reproduce
1. Generate a report for project "PROJECTOLDA" into a folder (file stem `bridge_report`).
2. Generate a report for project "PROJECTNEWB" into the same folder while `pdflatex` cannot run (e.g. LaTeX not installed / not on PATH).
Script: `scripts/probe_stale_pdf.py <outdir>`.

## Expected Behaviour
Step 2 returns `pdf_path=None` (and an error is shown), or removes/renames the old PDF before compiling.

## Actual Behaviour
Step 2 returns `pdf_path='.../bridge_report.pdf'`. The PDF is byte-identical to step 1 (same SHA-256, same modification time); the `.tex` contains PROJECTNEWB. The only trace is a log warning `pdflatex run failed: [Errno 2] No such file or directory: 'pdflatex'`. Reproduced twice in fresh processes.

## Root Cause
`src/osdagbridge/core/reports/report_generator.py:981-983`
```python
if os.path.exists(pdf_path):
    logger.info("Report generated: %s", pdf_path)
    return ReportResult(pdf_path=pdf_path, tex_path=tex_path)
```

## Suggested Fix
```diff
+        if os.path.exists(pdf_path):
+            os.remove(pdf_path)          # never let a previous report pass as the new one
         with tempfile.TemporaryDirectory() as tmp_dir:
 ...
-        if os.path.exists(pdf_path):
+        if os.path.exists(tmp_pdf) and res.returncode == 0:
```
(or compare the PDF's modification time with the start of the run).

## Duplicate Check
Searched all 210 issues for stale / old or previous PDF / pdflatex missing / `os.path.exists(pdf` / silent success. No match. (#104 = empty reactions table; #119 = chap7 group leak — unrelated.)
