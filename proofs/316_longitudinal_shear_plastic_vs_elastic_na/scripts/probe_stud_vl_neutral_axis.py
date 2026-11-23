"""Longitudinal shear VL (IRC 22:2015 Cl.606.4.1, irc22_2015.py:1753-1777) mixes the PLASTIC
neutral-axis depth xu with the ELASTIC composite inertia Ic:

    t_eff = min(xu, t_slab);  Aec = beff*t_eff/n;  Y = xu - t_eff/2;  VL = V*Aec*Y/Ic

The elastic shear-flow formula VL = V*A*ybar/I needs A and ybar about the ELASTIC neutral axis
of the same section that Ic belongs to. It also uses n = Es/Ecm (:1757) without the IRC 22
Cl.604.3 lower bound of 7.5 that the composite section properties use.

VL feeds the stud spacing (sl1) and the deck transverse-shear check (Cl.606.10, designer.py:1950).

--fix : recompute VL about the elastic neutral axis with the floored modular ratio.
usage: probe_stud_vl_neutral_axis.py <params.json> [--fix]
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
        orig = C.compute_stud_spacing
        def fixed(self, Vu_kN, beff_mm, xu_mm, Qu_kN, Ic_mm4=None):
            res = orig(self, Vu_kN, beff_mm, xu_mm, Qu_kN, Ic_mm4=Ic_mm4)
            sec, mat, slab = self.sec, self.mat, self.slab
            n = max(mat.Es / mat.Ecm, 7.5)                 # IRC 22 Cl.604.3 floor
            t = slab.thickness
            A_sl = beff_mm * t / n
            y_steel = t + (sec.D - sec.y_cg_from_bot)      # steel centroid from top of slab
            na = (A_sl * (t / 2.0) + sec.A_steel * y_steel) / (A_sl + sec.A_steel)
            ybar = na - t / 2.0                            # elastic NA to slab centroid
            VL = Vu_kN * 1e3 * A_sl * ybar / Ic_mm4
            res['VL_N_per_mm'] = round(VL, 3)
            res['spacing_mm'] = round(self.studs.n_per_section * Qu_kN * 1e3 / VL, 2)
            res['_elastic_NA_mm'] = round(na, 3)
            return res
        C.compute_stud_spacing = fixed

    p = json.load(open(sys.argv[1])); b = P(); b.set_input(R.build(p))
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        b.design()
    d = b.design_results
    dd = b.output_dict.get('deck_design_results', {})
    print('MODE', 'FIXED' if fix else 'ORIGINAL', '| span', d['span_m'], 'cw', d['carriageway_width_m'])
    print(f"GEOM xu(plastic)={d['xu_mm']:.3f}  elastic NA y_top={d['y_top_comp_mm']:.3f}"
          f"  t_slab={d['slab_thickness_mm']}  beff={d['beff_mm']}  Ic={d['I_comp_short_mm4']:.0f}")
    print(f"VL   {d['VL_N_per_mm']:.3f} N/mm   stud spacing sl1(ULS)={d['stud_spacing_uls_mm']:.2f}"
          f"  governing={d['stud_spacing_governing_mm']:.2f}  provided={d['stud_spacing_provided_mm']:.2f}")
    print(f"DECK transverse shear VL={d.get('steeldesign.transverse_shear.vl_kN_per_m')} kN/m"
          f"  Vrd={d.get('steeldesign.transverse_shear.vrd_kN_per_m')}"
          f"  Ast_req={d.get('Ast_required_cm2_per_m')} cm2/m  Ast_prov={d.get('Ast_provided_cm2_per_m')}"
          f"  ur={dd.get('ur_composite_trans_shear')}")


if __name__ == '__main__':
    main()
