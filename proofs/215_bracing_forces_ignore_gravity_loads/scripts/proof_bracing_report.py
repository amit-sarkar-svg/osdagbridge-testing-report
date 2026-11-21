"""Run a design (optionally with the Vy fix) and generate the full OsdagBridge PDF report, so the cross-bracing
member-force table can be shown as it appears to the user. Also saves the .tex and output_dict excerpt.
usage: proof_bracing_report.py <params.json> <outdir> [--vy]"""
import sys,json,io,contextlib,os
sys.path.insert(0,'/Users/macbook/Projects/OsdagBridge/src'); sys.path.insert(0,'/Users/macbook/Projects/osdagbridge-testing-report/scripts')
def main():
    import design_runner as R
    from osdagbridge.core.bridge_types.plate_girder.plategirderbridge import PlateGirderBridge as P
    from osdagbridge.core.bridge_types.plate_girder import crossbracingforces as CBF
    from osdagbridge.core.reports.report_generator import (ReportMetadata, ReportOptions, ReportRequest, build_report_payload, generate_report)
    vy='--vy' in sys.argv
    if vy:
        def read_vy(self, lc, member_id, is_i):
            comp="Vy_i" if is_i else "Vy_j"
            try: return float(self.bridge.result_data["forces"][str(lc)][member_id][comp])
            except (KeyError, TypeError, ValueError): return None
        CBF.CrossBracingForces._read_vz=read_vy
    p=json.load(open(sys.argv[1])); od=sys.argv[2]; os.makedirs(od,exist_ok=True)
    b=P(); b.set_input(R.build(p)); buf=io.StringIO()
    with contextlib.redirect_stdout(buf): b.design()
    json.dump(b.output_dict.get('crossbracing_forces_dict'),open(os.path.join(od,'crossbracing_forces_dict.json'),'w'),indent=1,default=str)
    md=ReportMetadata(project_name="Bracing forces "+("Vy fix" if vy else "original"),project_location="Ahmedabad",designer="QA",client="QA",company="QA",report_date="2026-11-22")
    req=ReportRequest(metadata=md,options=ReportOptions(sections=['design_checks'],include_figures=False,include_toc=True,include_pdf=True),output_dir=od,file_stem='bracing_report_'+('vy' if vy else 'original'))
    res=generate_report(build_report_payload(req,b.input_dict,b.output_dict),req)
    print('RESULT',res.pdf_path,res.tex_path)
if __name__=='__main__': main()
