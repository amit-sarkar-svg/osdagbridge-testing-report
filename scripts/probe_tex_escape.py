import sys,subprocess,tempfile,os
sys.path.insert(0,'/Users/macbook/Projects/OsdagBridge/src')
from osdagbridge.core.reports.report_utils import _tex
from osdagbridge.core.reports import chap8
print('TEX_BACKSLASH',repr(_tex("a\\b")),'expected',repr(r"a\textbackslash{}b"))
print('TEX_ANGLE',repr(_tex("a<b>|c")))
def compile_(body,label):
    d=tempfile.mkdtemp(dir='evidence/tmp'); open(d+'/t.tex','w').write("\\documentclass{article}\\usepackage{xcolor}\\begin{document}"+body+"\\end{document}")
    try:
        r=subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error','t.tex'],cwd=d,capture_output=True,text=True,timeout=60)
        print(label,'rc',r.returncode,'pdf',os.path.exists(d+'/t.pdf'))
    except subprocess.TimeoutExpired: print(label,'TIMEOUT')
import inspect
print(inspect.signature(chap8.ch8_design_log))
for line in ("INFO: ok","INFO: cost $5 and {x}","INFO: a ~ b ^ c \\ d"):
    try:
        tex=chap8.ch8_design_log([line],{})
        compile_(tex if isinstance(tex,str) else str(tex),f'CH8 {line!r}')
    except Exception as e: print('CH8',repr(line),'EXC',type(e).__name__,str(e)[:80])
