# Proof — #210: _tex() double-escapes backslashes, so "\" in report text prints as "\{}"

**Issue:** https://github.com/Nidhikhare12/OsdagBridge/issues/210  
**Severity:** S3 · Low (cosmetic) · **Tier:** T1 confirmed  
**Environment:** OsdagBridge `dev` @ `d74f56d` · macOS 13.6 (Darwin 22.6.0) · conda env `osdagbridge-env` · tested 2026-11-21

## Reproduce
```bash
source ~/miniconda3/etc/profile.d/conda.sh && conda activate osdagbridge-env
cd osdagbridge-testing-report
python proofs/210_tex_backslash_double_escape/scripts/probe_tex_escape.py
python proofs/210_tex_backslash_double_escape/scripts/l6_report_cases.py backslash
```

## Expected
`_tex('a\\b') == r'a\textbackslash{}b'` (prints a\b).

## Actual
`a\textbackslash\{\}b` (prints a\{}b).

## Evidence in this folder
| File | What it shows |
|---|---|
| `logs/probe_tex_escape.log` | `TEX_BACKSLASH` line, two runs, identical |
| `report_output/backslash_project_name.tex` | Full report for project name `A\textbf{B}`: header and table contain `A\textbackslash\{\}textbf\{B\}` |
| `report_output/backslash_project_name.pdf` | Compiled PDF of that report |
| `report_output/latex_input_injection_attempt.tex` | Security check: project name `\input{/etc/hostname}` is escaped, file not read (not an injection) |
| `logs/l6_report_cases.log` | All report free-text cases: normal, CJK, special chars, backslash, file stems, injection attempt |

## Root cause
`report_utils.py:18-23` escapes in sequential passes; the brace pass re-escapes the braces inserted by the backslash pass.

## Notes
In `logs/probe_tex_escape.log` the `CH8 ... rc 1` lines come from a minimal LaTeX harness without the report preamble (even the plain `INFO: ok` line fails) — they are a harness artefact and are **not** evidence for this issue. The OsdagBridge clone was never modified; fixes were proven by monkeypatching a copy inside the test scripts. The issue or comment text as drafted is in `ISSUE_210.md`.
