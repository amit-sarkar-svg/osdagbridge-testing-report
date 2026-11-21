#!/usr/bin/env python3
"""Headless report generation with CJK free-text metadata (Track H end-to-end)."""
import sys,json,os,traceback
sys.path.insert(0,'/Users/macbook/Projects/OsdagBridge/src')
from osdagbridge.core.reports.report_generator import (
    ReportMetadata, ReportOptions, ReportRequest, build_report_payload, generate_report)
OUT='/Users/macbook/Projects/osdagbridge-testing-report/evidence/logs/report_cjk'
os.makedirs(OUT,exist_ok=True)
inp=json.load(open('/Users/macbook/Projects/osdagbridge-testing-report/test_cases/built/base.json'))
out=json.load(open('/Users/macbook/Projects/osdagbridge-testing-report/dictionaries/SMOKE/output.json'))
md=ReportMetadata(project_name="Test Bridge",project_location="Ahmedabad",designer="Tester",
                  client="Client Org",company="Org",report_date="2026-11-18")
req=ReportRequest(metadata=md,options=ReportOptions(sections=[],include_figures=False,include_toc=False,include_pdf=True),
                  output_dir=OUT,file_stem='cjk_report')
try:
    payload=build_report_payload(req,inp,out)
    print('PAYLOAD_OK')
    res=generate_report(payload,req)
    print('GENERATE_RESULT',str(res)[:200])
except Exception as e:
    print('EXCEPTION',type(e).__name__,str(e)[:200])
    traceback.print_exc()
print('PDF_EXISTS',os.path.exists(os.path.join(OUT,'cjk_report.pdf')))
