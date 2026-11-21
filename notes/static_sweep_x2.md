# Stage 2 static sweep (X2, 2026-11-21, clone dev@d74f56d) — all T3 unless stated
bandit (evidence/logs/bandit.json): 232 findings = 222 LOW, 10 MEDIUM, 0 HIGH. Non-B101: B110 try/except/pass x179, B311 random x20 (deck/builder.py:192-229, non-security), B608 SQL string x10, B112 except/continue x8, B404/B603/B607 subprocess x8, B105 x2, B606 x1.
ruff (F,B): F405 2475 (star imports), F401 226, F811 79, F841 62, B008 23 (function call in default arg), B023 7, B904 6.
pip-audit: no known vulnerabilities; navcube/osdag/osdag-core/osdagbridge not auditable (local, T5 note).
| file:line | risk | verdict |
| yaml.dump unsafe tags template_page.py:812 | load/save asymmetry | known #131 (T4) |
| yaml.safe_load template_page.py:839 | safe loader | T8 |
| eval ospgrillage/utils.py:338, osp_grillage.py:120,622,625 | eval of internally generated repr strings | T3 low, fragile not exploitable from UI input |
| exec ospgrillage/ospgui.py:1861 | GUI-only, not reachable from analyser | T3 |
| SQL f-string common.py:1519,1781, metadata_mapper.py:48(table), database.py:93 | table names interpolated; values parametrised | T3, need to confirm table names are constants (reading by subagent: internal) |
| pdflatex report_generator.py:865-985 | list args, no shell=True, no -shell-escape, TemporaryDirectory | T8; no timeout (C11, T3); stale PDF returned on failure (C09) |
| pickle, os.system, mktemp, shell=True | no hits | T8 |
| file_stem from basename(output_path) | no traversal; spaces/&/leading - break pdflatex | C09/C10 needs test |
No harmless-proof executed for LaTeX injection: pdflatex absent check not done in this session (T9).
