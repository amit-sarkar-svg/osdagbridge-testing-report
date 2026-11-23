"""Run a design with an optional test-only fix applied, then generate OsdagBridge's own PDF report.

patch = none  : program as shipped
        sidl  : call the never-called create_sidl_combination() before create_dead_load_combination()
        betab : correct the operator precedence in cl_8_2_1_2_design_bending_strength

usage: proof_report_variant.py <params.json> <outdir> <none|sidl|betab>
"""
import sys, json, io, contextlib, os
sys.path.insert(0, '/Users/macbook/Projects/OsdagBridge/src')
sys.path.insert(0, '/Users/macbook/Projects/osdagbridge-testing-report/scripts')


def main():
    import design_runner as R
    from osdagbridge.core.bridge_types.plate_girder.plategirderbridge import PlateGirderBridge as P
    from osdagbridge.core.utils.codes import irc22_2015 as IRCMOD
    import osdagbridge.core.utils.codes.is800_2007 as M
    from osdagbridge.core.reports.report_generator import (
        ReportMetadata, ReportOptions, ReportRequest, build_report_payload, generate_report)
    params, od, patch = sys.argv[1], sys.argv[2], sys.argv[3]
    os.makedirs(od, exist_ok=True)

    if patch == 'sidl':
        orig = P.add_dead_loads
        def patched(self):
            gm = self.grillage_model; real = gm.create_dead_load_combination
            def deferred(*a, **k):
                gm.create_sidl_combination(); return real(*a, **k)
            gm.create_dead_load_combination = deferred
            try: return orig(self)
            finally: gm.create_dead_load_combination = real
        P.add_dead_loads = patched
    elif patch == 'betab':
        def fixed(section_class, Zp, Ze, fy, gamma_mo, support):
            sc = str(section_class).strip().lower()
            beta_b = 1.0 if sc in ('plastic', 'compact') else Ze / Zp
            cap = (1.2 if support == M.KEY_DISP_SUPPORT1 else 1.5) * Ze * fy / gamma_mo
            return min(beta_b * Zp * fy / gamma_mo, cap)
        IRCMOD.IS800_2007.cl_8_2_1_2_design_bending_strength = staticmethod(fixed)

    p = json.load(open(params)); b = P(); b.set_input(R.build(p))
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        b.design()
    d = b.design_results
    print('PATCH', patch, 'Mu', d.get('Mu_kNm'), 'Vu', d.get('Vu_kN'),
          'Mb_stage1', d.get('Mb_kNm_stage1'), 'Mb', d.get('Mb_kNm'),
          'max_dcr', d.get('max_dcr'), d.get('overall_status'))
    md = ReportMetadata(project_name={'none': 'As shipped', 'sidl': 'With SIDL in DL',
                                      'betab': 'With beta_b fixed'}[patch],
                        project_location="Ahmedabad", designer="QA", client="QA",
                        company="QA", report_date="2026-11-24")
    req = ReportRequest(metadata=md,
                        options=ReportOptions(sections=['loads', 'analysis', 'design_checks'],
                                              include_figures=False, include_toc=True, include_pdf=True),
                        output_dir=od, file_stem='report_' + patch)
    res = generate_report(build_report_payload(req, b.input_dict, b.output_dict), req)
    print('RESULT', res.pdf_path)


if __name__ == '__main__':
    main()
