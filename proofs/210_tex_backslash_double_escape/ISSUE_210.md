# [Bug/Report] `_tex()` escapes a backslash as `\textbackslash\{\}`, so a "\" in user text prints as "\{}" in the PDF

**Environment:** macOS 13.6 (Darwin 22.6.0), Python (conda env `osdagbridge-env`), OsdagBridge branch `dev`, commit `d74f56d`.

## Description
`report_utils._tex` (`report_utils.py:18-23`) first replaces `\` with `\textbackslash{}`, then escapes `{` and `}` in the same string. That turns the braces it has just inserted into literal braces. Any backslash in a free-text field, such as a project name or client, is printed as `\{}`. The characters `<`, `>` and `|` are also passed through unescaped (`_tex("a<b>|c")` returns `'a<b>|c'`). I did not check how they render.

## Steps to reproduce
```python
from osdagbridge.core.reports.report_utils import _tex
_tex("a\\b")   # returns 'a\textbackslash\{\}b'
```
End to end: generate a report with project name `A\textbf{B}`. The `.tex` contains `A\textbackslash\{\}textbf\{B\}` (`scripts/l6_report_cases.py backslash`).

## Expected
`a\textbackslash{}b`, which prints "a\b".

## Actual
`a\textbackslash\{\}b`, which prints "a\{}b". Reproduced in two processes (`evidence/logs/probe_tex_escape.log`).

## Suggested fix
```diff
-    s = s.replace('\\', r'\textbackslash{}')
-    for ch, esc in [('&', r'\&'), ..., ('{', r'\{'), ('}', r'\}'), ...]:
-        s = s.replace(ch, esc)
+    table = {'\\': r'\textbackslash{}', '&': r'\&', '%': r'\%', '$': r'$', '#': r'\#',
+             '{': r'\{', '}': r'\}', '_': r'\_\allowbreak{}', '~': r'\textasciitilde{}',
+             '^': r'\^{}', '<': r'\textless{}', '>': r'\textgreater{}', '|': r'\textbar{}'}
+    s = ''.join(table.get(c, c) for c in s)
```
This is a single-pass translation, so escapes are never re-escaped.

## Security note
I tested `\input{/etc/hostname}` as a project name. It is escaped correctly, and the file is not read (`evidence/logs/l6_report_cases.log`). This is a cosmetic issue, not an injection.

## Duplicate check
I searched titles and bodies for `_tex(`, backslash, textbackslash and escape. The hits were #70, #75 and #192. #70 mentions `_tex()` only for missing units, so it is not the backslash double-escape.
