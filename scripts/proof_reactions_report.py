"""Generate the PDF report from a saved design state exactly as PlateGirderBridge.generate_design_report does
(output_dict['analysis_summary'] = {'load_cases': _lc_summary, 'reactions': _reaction_summary}) and extract the
'Reactions at Supports' rows. usage: proof_reactions_report.py <case_dir> <outdir>"""
import sys,json,os,re
sys.path.insert(0,'/Users/macbook/Projects/OsdagBridge/src')
def main():
    from osdagbridge.core.reports.report_generator import (ReportMetadata, ReportOptions, ReportRequest, build_report_payload, generate_report)
    cd,od=sys.argv[1],sys.argv[2]; os.makedirs(od,exist_ok=True)
    st=json.load(open(cd+'/state.json')); inp=json.load(open(cd+'/input.json'))
    out=dict(st['output_dict']); out['analysis_summary']={'load_cases':st['_lc_summary'] or {},'reactions':st['_reaction_summary'] or {}}
    md=ReportMetadata(project_name="Reactions proof",project_location="Ahmedabad",designer="QA",client="QA",company="QA",report_date="2026-11-21")
    req=ReportRequest(metadata=md,options=ReportOptions(sections=['analysis'],include_figures=False,include_toc=False,include_pdf=True),output_dir=od,file_stem='reactions_report')
    res=generate_report(build_report_payload(req,inp,out),req); print('RESULT',res.pdf_path)
    tex=open(res.tex_path).read()
    i=tex.find('Reactions at Supports'); blk=tex[i:i+6000]
    for lc in ('SW','1.0 DL','1.0 DW','Crash barrier load','SLS\\_QP\\_1','BASIC\\_1'):
        for line in blk.splitlines():
            if line.strip().startswith(lc+' &') or line.strip().startswith(lc.replace('\\_','_')+' &'): print('ROW',line.strip()[:120])
if __name__=='__main__': main()
