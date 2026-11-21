"""Stale-PDF lead: generate report A (normal), then regenerate report B with a different project name into the same folder
while pdflatex cannot run (PATH without TeX). usage: probe_stale_pdf.py <outdir>"""
import sys,json,os,hashlib,subprocess
R='/Users/macbook/Projects/osdagbridge-testing-report/'
CHILD=r'''
import sys,json,os
sys.path.insert(0,'/Users/macbook/Projects/OsdagBridge/src')
from osdagbridge.core.reports.report_generator import (ReportMetadata, ReportOptions, ReportRequest, build_report_payload, generate_report)
R='/Users/macbook/Projects/osdagbridge-testing-report/'
od,name=sys.argv[1],sys.argv[2]
inp=json.load(open(R+'test_cases/built/base.json')); out=json.load(open(R+'dictionaries/SMOKE/output.json'))
md=ReportMetadata(project_name=name,project_location="Ahmedabad",designer="QA",client="QA",company="QA",report_date="2026-11-21")
req=ReportRequest(metadata=md,options=ReportOptions(sections=[],include_figures=False,include_toc=False,include_pdf=True),output_dir=od,file_stem='bridge_report')
res=generate_report(build_report_payload(req,inp,out),req)
print('RESULT_PDF',res.pdf_path); print('RESULT_TEX',res.tex_path)
'''
def h(p): return hashlib.sha256(open(p,'rb').read()).hexdigest()[:16] if os.path.exists(p) else None
def main():
    od=sys.argv[1]; os.makedirs(od,exist_ok=True); c=os.path.join(od,'_child.py'); open(c,'w').write(CHILD)
    pdf=os.path.join(od,'bridge_report.pdf'); tex=os.path.join(od,'bridge_report.tex')
    a=subprocess.run([sys.executable,c,od,'PROJECTOLDA'],capture_output=True,text=True,timeout=300)
    print('STEP1 normal run:', [l for l in a.stdout.splitlines() if l.startswith('RESULT')], 'pdf sha', h(pdf))
    pdf_a=h(pdf); mt_a=os.path.getmtime(pdf)
    env=dict(os.environ); env['PATH']='/usr/bin:/bin'   # no TeX on PATH
    b=subprocess.run([sys.executable,c,od,'PROJECTNEWB'],capture_output=True,text=True,timeout=300,env=env)
    print('STEP2 no-TeX run:', [l for l in b.stdout.splitlines() if l.startswith('RESULT')])
    print('STEP2 pdf sha', h(pdf), 'unchanged_from_step1', h(pdf)==pdf_a, 'mtime_unchanged', os.path.getmtime(pdf)==mt_a)
    t=open(tex).read(); print('STEP2 tex has NEW name', 'PROJECTNEWB' in t, '| tex has OLD name', 'PROJECTOLDA' in t)
    print('STEP2 warnings:', [l[:120] for l in b.stderr.splitlines() if 'pdflatex' in l.lower() or 'generated' in l.lower()][:3])
if __name__=='__main__': main()
