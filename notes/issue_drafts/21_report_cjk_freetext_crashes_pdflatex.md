# [Bug/Report] Non-Latin (CJK) free-text in report metadata causes 39 LaTeX errors; generator still reports success with dropped glyphs

**Environment**
- OsdagBridge `dev` @ `d74f56d` (2026-07-26)
- macOS (Intel), conda env `osdagbridge-env`; pdflatex (TeX Live 2025)
- Static + executed LaTeX compile (no full design needed)
- Finding type: **T2 (likely bug — report generation fails on valid user input)**

**Description**
The report escapes LaTeX special characters via `_tex()` in `report_utils.py`, but that function only normalizes three Unicode glyphs (`∠`, `ⅹ`, `×`) and passes other non-ASCII characters through unchanged. When a user types non-Latin text (e.g. CJK such as `日本`) into a free-text metadata field that is inserted via `_tex()` — **Project Name, Project Location, Author/Designer, Reviewer, Organization, Client, Job Number** — the generated LaTeX contains raw CJK characters and `pdflatex` aborts with `! LaTeX Error: Unicode character 日 (U+65E5) not set up for use with LaTeX`, producing **no PDF**.

**When it works vs fails**
- Works: ASCII specials are fully escaped (`A&B`→`A\&B`, `50%`→`50\%`, `_`, `#`, `{`, `}`, `$`, `~`, `^`, `\` all handled); Latin accents (`é ü ñ café naïve`) compile fine under modern pdflatex (tested, exit 0).
- Fails: any CJK / non-Latin character in a `_tex()`-inserted field → pdflatex fatal error.

**Steps / Reproduction (executed)**
1. Take the strings `A&B`, `50%`, `item_1`, `#1`, `{x}`, `a\b`, `$5`, `~`, `^`, `é ü ñ`, `日本`, and a 300-char string.
2. Escape with `osdagbridge.core.reports.report_utils._tex` (used for all report metadata fields).
3. Build a LaTeX doc using the report's own packages and run `pdflatex`.

Observed: ASCII specials and Latin accents compile (exit 0); the doc containing `日本` fails:
```
! LaTeX Error: Unicode character 日 (U+65E5)
   not set up for use with LaTeX.
==> Fatal error occurred, no output PDF file produced!
```
Evidence: `evidence/logs/tex_test/specialchars.tex`, `specialchars.log` (CJK failure), `latin.tex`/`latin.log` (Latin accents OK).

**Expected vs actual (justification)**
- **Expected:** free-text a user can type into the GUI should not make report generation fail; non-Latin text should either render (e.g. via XeLaTeX/`\usepackage[CJK]{...}`) or be transliterated/stripped with a clear message rather than aborting.
- **Actual:** raw CJK reaches the `.tex` and pdflatex aborts; no PDF.

**Root cause (file:line, read-only)**
`src/osdagbridge/core/reports/report_utils.py` `_tex()` (~L10-25) escapes ASCII specials and maps only `∠`,`ⅹ`,`×`; no handling for other non-ASCII. Every metadata field passes through it: `report_generator.py` cover table (≈L319-329) e.g. `\textbf{Project Name} & _tex(m.project_name)`; also `preamble()` (≈L150) via `_tex(project_name)`.

**Suggested fix (diff idea)**
```diff
 def _tex(value):
     s = str(value) if value is not None else ''
     ...
+    # Transliterate/strip characters the engine cannot render, or switch to XeLaTeX.
+    s = ''.join(ch if ord(ch) < 128 else ('?' if ord(ch) > 0x024F else ch) for ch in s)
     s = s.replace('\\', r'\textbackslash{}')
```
(or configure the report to compile with XeLaTeX + a CJK-capable font, which renders non-Latin text properly.)

**Duplicate check**
Searched refreshed issues (146 items, 83 issues, `notes/issues_raw.json`) via `scripts/search_issues.py`: #70 covers a dropped `≤` math symbol (ASCII/Unicode math), a different trigger; #121 covers missing `\endhead` on multi-page tables; no issue covers CJK/non-Latin free-text crashing pdflatex. **New trigger condition — no duplicate.**

**Notes**
Reported as T2 (likely) because the failure is reproduced on a minimal doc using the project's own `_tex()` and pdflatex; the full GUI report call was not run (no baseline.osi), but the exact failing path (`_tex` → `.tex` → pdflatex) is the one the report generator uses. Latin accents are explicitly shown to work, so the bug is specific to non-Latin scripts.


**UPDATE — executed end-to-end via `build_report_payload` + `generate_report` (stronger evidence)**
`scripts/report_cjk_clean.py` built a real report with `project_name="日本 Bridge"`, `client="Client 日本"` from the completed SMOKE dict. Result: `generate_report` returned `ReportResult(pdf_path=...)` with no error surfaced to the caller and `PDF_EXISTS True` — i.e. the app reports **success** (exit 0 from the harness). But compiling the generated `.tex` directly:
```
pdflatex -interaction=nonstopmode cjk_report.tex  -> EXIT 1, 39 "Unicode character ... not set up" errors
Output written on cjk_report.pdf (16 pages, 184347 bytes).
```
The raw CJK appears in the `.tex` (lines 59/77/146: `日本 Bridge`). Because `generate_report` runs `pdflatex -interaction=nonstopmode` with `check=False` and only tests `os.path.exists(pdf)` (report_generator.py:969-980), the 39 LaTeX errors are swallowed: the user gets a PDF with the CJK glyphs silently dropped and **no warning**. The minimal test with `-halt-on-error` gave "no PDF"; the real generator's nonstopmode gives a partial PDF reported as success.
Evidence: `scripts/report_cjk_clean.py`, `evidence/logs/report_cjk_clean.log`, `evidence/logs/cjk_clean/cjk_report.tex`, `evidence/logs/cjk_clean/compile.log` (39 errors).

**Root cause (second part):** `src/osdagbridge/core/reports/report_generator.py:969-980` — `res = subprocess.run([compiler, '-interaction=nonstopmode', ...], check=False)` then `if os.path.exists(tmp_pdf): copy2(...)` and success is returned without inspecting `res.returncode` or the log for `! LaTeX Error`. So any LaTeX error (CJK here, `≤` from #70, missing glyphs) yields a silently-degraded PDF marked successful.
