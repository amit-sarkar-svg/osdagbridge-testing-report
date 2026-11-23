"""M-V interaction (IRC 22 Cl.603.3.3.3 / IS 800 Cl.9.2.2) is fed the PLASTIC shear capacity
Vd instead of the governing design shear strength, which for these slender webs is the shear
buckling resistance Vcr.

designer.py:1826 calls compute_combined_bending_shear(Md, Vu, results.Vd_kN). results.Vd_kN is
the plastic value from compute_shear_capacity() (:1762); the buckling value results.Vcr_kN
(:1785) is what the "ULS Shear Buckling" check and the report use as the shear capacity.
High shear therefore triggers at V > 0.6*Vd_plastic instead of V > 0.6*Vcr.

--fix : clamp Vd_kN to min(Vd_kN, Vcr_kN) at the interaction call.
usage: probe_mv_interaction_vd.py <params.json> [--fix]
"""
import sys, json, io, contextlib
sys.path.insert(0, '/Users/macbook/Projects/OsdagBridge/src')
sys.path.insert(0, '/Users/macbook/Projects/osdagbridge-testing-report/scripts')


def main():
    import design_runner as R
    from osdagbridge.core.bridge_types.plate_girder import designer as D
    from osdagbridge.core.bridge_types.plate_girder.plategirderbridge import PlateGirderBridge as P
    fix = '--fix' in sys.argv
    if fix:
        C = D.IRC22CapacityCalculator
        buck, inter = C.compute_shear_buckling, C.compute_combined_bending_shear
        def buck_rec(self, *a, **k):
            res = buck(self, *a, **k)
            self._seen_vcr = res["Vcr_kN"]
            return res
        def inter_fix(self, Md_kNm, V_kN, Vd_kN):
            vcr = getattr(self, '_seen_vcr', None)
            if vcr:
                Vd_kN = min(Vd_kN, vcr)      # governing design shear strength
            return inter(self, Md_kNm, V_kN, Vd_kN)
        C.compute_shear_buckling = buck_rec
        C.compute_combined_bending_shear = inter_fix

    p = json.load(open(sys.argv[1])); b = P(); b.set_input(R.build(p))
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        b.design()
    d = b.design_results
    V, Vcr, Vd = d['Vu_kN'], d['Vcr_kN'], d['Vd_kN']
    print('MODE', 'FIXED' if fix else 'ORIGINAL', '| span', d['span_m'], 'cw', d['carriageway_width_m'])
    print(f'SHEAR Vu={V:.2f}  Vcr(buckling, governing)={Vcr:.2f}  Vd(plastic)={Vd:.2f}'
          f'  0.6Vcr={0.6*Vcr:.1f}  0.6Vd={0.6*Vd:.1f}  high-shear per IS800={V > 0.6*Vcr}')
    print(f'INTERACTION beta={d["beta_interaction"]}  Md={d["Md_kNm"]:.2f}  Mdv={d["Mdv_kNm"]:.2f}'
          f'  Mu={d["Mu_kNm"]:.2f}')
    for c in d['checks']:
        if c['name'] in ('ULS Flexure', 'ULS Shear Buckling', 'M-V Interaction'):
            print(f'CHECK {c["name"]:22} D={c["demand"]:<10} C={c["capacity"]:<11} dcr={c["dcr"]:<8} {c["status"]}')
    print('OVERALL max_dcr', d['max_dcr'], d['overall_status'])


if __name__ == '__main__':
    main()
