"""L6: report cases in fresh subprocesses. usage: l6_report_cases.py <case>"""
import sys,json,os,shutil,tempfile
sys.path.insert(0,'/Users/macbook/Projects/OsdagBridge/src')
from osdagbridge.core.reports.report_generator import (ReportMetadata, ReportOptions, ReportRequest, build_report_payload, generate_report)
R='/Users/macbook/Projects/osdagbridge-testing-report/'
inp=json.load(open(R+'test_cases/built/base.json')); out=json.load(open(R+'dictionaries/SMOKE/output.json'))
case=sys.argv[1]
name,stem,pre="Bridge","rep",False
if case=='normal': pass
elif case=='stale_cjk': name,pre="日本 Bridge",True
elif case=='special': name="50% $x_1 {a} ~ ^ # & <b> |"
elif case=='backslash': name=r"A\textbf{B}"
elif case=='stem_space': stem="my report"
elif case=='stem_amp': stem="&foo"
elif case=='stem_dash': stem="-foo"
elif case=='latex_input': name=r"\input{/etc/hostname}"
od=tempfile.mkdtemp(prefix='l6_',dir=R+'evidence/tmp')
if pre: open(os.path.join(od,stem+'.pdf'),'wb').write(b'OLD')
md=ReportMetadata(project_name=name,project_location="Ahmedabad",designer="T",client="C",company="O",report_date="2026-11-21")
req=ReportRequest(metadata=md,options=ReportOptions(sections=[],include_figures=False,include_toc=False,include_pdf=True),output_dir=od,file_stem=stem)
try:
    res=generate_report(build_report_payload(req,inp,out),req)
    print('RESULT',str(res)[:300])
except Exception as e: print('EXC',type(e).__name__,str(e)[:200])
p=os.path.join(od,stem+'.pdf')
print('PDF_EXISTS',os.path.exists(p),'SIZE',os.path.getsize(p) if os.path.exists(p) else 0,'STALE_BYTES',open(p,'rb').read(3)==b'OLD' if os.path.exists(p) else None)
print('FILES',sorted(os.listdir(od))[:8])
