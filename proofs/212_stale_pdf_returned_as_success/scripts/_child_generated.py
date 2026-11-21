
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
