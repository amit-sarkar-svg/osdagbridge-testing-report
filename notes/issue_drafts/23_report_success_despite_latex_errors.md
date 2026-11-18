# [Bug/Report] `generate_report` reports success even when pdflatex has fatal errors and drops content

**Environment**
- OsdagBridge `dev` @ `d74f56d` (2026-07-26)
- macOS (Intel), conda env `osdagbridge-env`, TeX Live 2026 pdflatex
- Headless `build_report_payload` + `generate_report` from a completed SMOKE design dict
- Finding type: **T2 (likely bug — silently degraded output reported as success)**

**Description**
`generate_report()` compiles the generated LaTeX with `pdflatex -interaction=nonstopmode` using `subprocess.run(..., check=False)`, and declares success based solely on `os.path.exists(pdf)`. It never inspects `res.returncode` or the compiler log for `! LaTeX Error`. Consequently, when the LaTeX has fatal errors (e.g. an unsupported Unicode character, or the dropped `≤` of #70), pdflatex exits non-zero after emitting a partial PDF in nonstopmode, but the generator still returns a successful `ReportResult` with no warning. The user receives a degraded PDF (glyphs/checks missing) believing generation succeeded.

**When it works vs fails**
- Works: clean LaTeX → pdflatex exit 0 → complete PDF, success correctly reported.
- Fails: any LaTeX error that nonstopmode recovers from by dropping content → exit 1 but PDF exists → success incorrectly reported, errors swallowed.

**Steps / Reproduction (executed)**
1. Build a report with `project_name="日本 Bridge"`, `client="Client 日本"` using the completed SMOKE input/output dicts (`scripts/report_cjk_clean.py`).
2. `build_report_payload(req, inp, out)` → `generate_report(payload, req)`.
3. Observe `generate_report` returns `ReportResult(pdf_path=..., tex_path=...)` (success, no exception) and `PDF_EXISTS True`.
4. Compile the generated `.tex` directly: `pdflatex -interaction=nonstopmode cjk_report.tex` → **EXIT 1, 39 "Unicode character ... not set up" errors**, yet `Output written on cjk_report.pdf (16 pages, 184347 bytes)`.

**Expected vs actual (justification)**
- **Expected:** if pdflatex exits non-zero or the log contains `! LaTeX Error`, report generation should fail (or at least warn) — a silently incomplete engineering report is unsafe.
- **Actual:** `check=False` + existence-only success hides all compiler errors; the degraded PDF is reported as a normal result.

**Logs and proof**
- `scripts/report_cjk_clean.py`, `evidence/logs/report_cjk_clean.log` (success returned), `evidence/logs/cjk_clean/cjk_report.tex` (raw CJK at L59/77/146), `evidence/logs/cjk_clean/compile.log` (39 Unicode errors, exit 1).
- Code: `report_generator.py:969-980` (subprocess `check=False`, `if os.path.exists(tmp_pdf): copy2`, success return).

**Root cause (file:line, read-only)**
`src/osdagbridge/core/reports/report_generator.py` ≈L969-982:
```py
res = subprocess.run([compiler, '-interaction=nonstopmode', request.file_stem + '.tex'], ... check=False)
...
if os.path.exists(tmp_pdf):
    shutil.copy2(tmp_pdf, pdf_path)
...
if os.path.exists(pdf_path):
    return ReportResult(pdf_path=pdf_path, tex_path=tex_path)   # success despite res.returncode != 0
```

**Suggested fix (diff idea)**
```diff
     if os.path.exists(pdf_path):
+        log = ...
+        if res.returncode != 0 or (log and '! LaTeX Error' in log):
+            raise RuntimeError(f"LaTeX compilation reported errors (exit {res.returncode}); "
+                               "report is incomplete. See diagnostics log.")
         return ReportResult(pdf_path=pdf_path, tex_path=tex_path)
```
(The codebase already has diagnostic-log helpers per #34's PR description — reuse them and surface the error to the caller instead of returning a degraded PDF as success.)

**Duplicate check**
Searched refreshed issues (146 items, 83 issues) via `scripts/search_issues.py` for `success`+`pdflatex`, `error`+`report`, `diagnostic` — no existing issue about success-despite-LaTeX-errors. #70 covers a dropped `≤` symbol (a trigger of the error), and #34/PRs discuss diagnostic handling in report generation but none flags this silent-success path. **No duplicate found.**

**Notes**
Reported as T2 (likely) because executed end-to-end with a real `generate_report` call and direct pdflatex verification; the fix location is clear. Related to #70 (one error trigger) and to the CJK-escape finding (draft 21) but distinct: this is about error detection/reporting, independent of which character caused it.
