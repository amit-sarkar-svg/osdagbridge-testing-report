"""#208 end-to-end: full report generation with design_log markers in output_dict; check .tex (and PDF text if pypdf present).
usage: proof_208_report_e2e.py <outdir>"""
import sys,json,os
sys.path.insert(0,'/Users/macbook/Projects/OsdagBridge/src')
from osdagbridge.core.reports.report_generator import (ReportMetadata, ReportOptions, ReportRequest, build_report_payload, generate_report)
R='/Users/macbook/Projects/osdagbridge-testing-report/'
od=sys.argv[1]; os.makedirs(od,exist_ok=True)
inp=json.load(open(R+'test_cases/built/base.json')); out=json.load(open(R+'dictionaries/SMOKE/output.json'))
markers=["INFO: Stage 1 complete MARKERINFOA","WARNING: Deck crack width check skipped MARKERWARNB","ERROR: Bearing stiffener check failed MARKERERRC"]
out['design_log']=markers
md=ReportMetadata(project_name="Proof 208",project_location="Ahmedabad",designer="QA",client="QA",company="QA",report_date="2026-11-21")
req=ReportRequest(metadata=md,options=ReportOptions(sections=[],include_figures=False,include_toc=False,include_pdf=True),output_dir=od,file_stem='report_208')
payload=build_report_payload(req,inp,out)
print('PAYLOAD log_entries =',payload.log_entries)
res=generate_report(payload,req); print('RESULT',res)
tex=open(res.tex_path).read()
for m in ('MARKERINFOA','MARKERWARNB','MARKERERRC'): print('TEX contains',m,'->',m in tex)
try:
    import pypdf
    txt=''.join(p.extract_text() or '' for p in pypdf.PdfReader(res.pdf_path).pages)
    for m in ('MARKERINFOA','MARKERWARNB','MARKERERRC'): print('PDF contains',m,'->',m in txt)
    print('PDF pages',len(pypdf.PdfReader(res.pdf_path).pages))
except ImportError: print('pypdf not installed: PDF text check skipped')
