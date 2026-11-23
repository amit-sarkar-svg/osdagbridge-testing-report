"""IS800_2007.cl_8_2_1_2_design_bending_strength (is800_2007.py:1026):

    beta_b = 1.0 if section_class == KEY_Plastic or KEY_Compact else Ze/Zp

Python parses this as (section_class == KEY_Plastic) or KEY_Compact. KEY_Compact
is the non-empty string "Compact", so the condition is ALWAYS true and beta_b is
always 1.0: Semi-Compact and Slender sections get the full plastic moment.

--fix : monkeypatch the function with the intended precedence
        (beta_b = 1.0 for Plastic/Compact, else Ze/Zp), case-insensitive.
usage: probe_beta_b_precedence.py <params.json> [--fix]
"""
import sys, json, io, contextlib
sys.path.insert(0, '/Users/macbook/Projects/OsdagBridge/src')
sys.path.insert(0, '/Users/macbook/Projects/osdagbridge-testing-report/scripts')


def main():
    import design_runner as R
    import osdagbridge.core.utils.codes.is800_2007 as M
    from osdagbridge.core.utils.codes import irc22_2015 as IRCMOD
    import inspect
    IS800_2007 = IRCMOD.IS800_2007          # the copy IRC22 actually calls
    print('TARGET IS800_2007 from', IS800_2007.__module__, '|', inspect.getsourcefile(IS800_2007))
    from osdagbridge.core.bridge_types.plate_girder.plategirderbridge import PlateGirderBridge as P
    fix = '--fix' in sys.argv
    if fix:
        def fixed(section_class, Zp, Ze, fy, gamma_mo, support):
            sc = str(section_class).strip().lower()
            beta_b = 1.0 if sc in ('plastic', 'compact') else Ze / Zp
            Md = beta_b * Zp * fy / gamma_mo
            cap = (1.2 if support == M.KEY_DISP_SUPPORT1 else 1.5) * Ze * fy / gamma_mo
            return min(Md, cap)
        IS800_2007.cl_8_2_1_2_design_bending_strength = staticmethod(fixed)

    p = json.load(open(sys.argv[1])); b = P(); b.set_input(R.build(p))
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        b.design()
    d = b.design_results
    print('MODE', 'FIXED' if fix else 'ORIGINAL', '| span', d['span_m'], 'fy', d['fy_MPa'])
    print('CLASS web=%s flange=%s governing=%s  (d/tw=%s limit=%s)'
          % (d['section_class_web'], d['section_class_flange'], d['section_class_governing'],
             d['d_tw_ratio'], d['web_class_limit']))
    print('MODULI Zp=%.0f Ze=%.0f  Ze/Zp=%.4f' % (d['Zp_steel_mm3'], d['Ze_steel_mm3'],
                                                  d['Ze_steel_mm3'] / d['Zp_steel_mm3']))
    print('LTB  Mb_stage1=%.3f (chi=%.4f)  Mb_stage2=%.3f (chi=%.4f)'
          % (d['Mb_kNm_stage1'], d['chi_LT_stage1'], d['Mb_kNm'], d['chi_LT']))
    print('IMPLIED Mpl_stage1 = Mb/chi = %.2f kNm' % (d['Mb_kNm_stage1'] / d['chi_LT_stage1']))
    for c in d['checks']:
        if 'LTB' in c['name']:
            print('CHECK %-28s D=%-10s C=%-10s dcr=%-7s %s'
                  % (c['name'], c['demand'], c['capacity'], c['dcr'], c['status']))
    print('OVERALL max_dcr', d['max_dcr'], d['overall_status'])


if __name__ == '__main__':
    main()
