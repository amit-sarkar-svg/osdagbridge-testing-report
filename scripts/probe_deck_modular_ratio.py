"""Deck slab SLS: record the Es/Ecm actually passed to deckdesign._cracked_section during a real design,
and recompute the cracked section by hand. --fix: monkeypatch Ecm given in GPa (<1000) to MPa.
usage: probe_deck_modular_ratio.py <params.json> [--fix]"""
import sys,json,io,contextlib,math
sys.path.insert(0,'/Users/macbook/Projects/OsdagBridge/src'); sys.path.insert(0,'/Users/macbook/Projects/osdagbridge-testing-report/scripts')
def main():
    import design_runner as R
    from osdagbridge.core.bridge_types.plate_girder import deckdesign as DD
    from osdagbridge.core.bridge_types.plate_girder.plategirderbridge import PlateGirderBridge as P
    calls=[]; orig=DD._cracked_section
    def rec(As_mm2,d_mm,Es_MPa,Ecm_MPa,b_mm=1000.0):
        if '--fix' in sys.argv and Ecm_MPa<1000: Ecm_MPa=Ecm_MPa*1000.0
        r=orig(As_mm2,d_mm,Es_MPa,Ecm_MPa,b_mm); calls.append((As_mm2,d_mm,Es_MPa,Ecm_MPa,r)); return r
    DD._cracked_section=rec
    p=json.load(open(sys.argv[1])); b=P(); b.set_input(R.build(p)); buf=io.StringIO()
    with contextlib.redirect_stdout(buf): b.design()
    print('MODE','FIX' if '--fix' in sys.argv else 'ORIGINAL','material concrete',b.material_props.concrete_prop)
    seen=set()
    for As,d,Es,Ecm,(x,I,ae) in calls:
        k=(round(As),round(d,1))
        if k in seen: continue
        seen.add(k); print(f'CALL As={As:.0f} mm2/m d={d:.1f} mm Es={Es} Ecm={Ecm} -> alpha_e={ae:.2f} x={x:.1f} mm ({x/d*100:.0f}% of d) I_cr={I:.3e}')
    dd=b.output_dict['deck_design_results']
    print('RESULT', {k:dd.get(k) for k in ('rebar_bottom_dia','rebar_bottom_spacing','rebar_bottom_area','rebar_top_spacing','rebar_top_area','rebar_overhang_spacing','rebar_overhang_area','deckdesign.stress.concrete.bottom','deckdesign.stress.reinf.bottom','deckdesign.stress.concrete.top','deckdesign.stress.reinf.top','deckdesign.crack.wk.bottom','deckdesign.crack.wk.top','ur_bot_sls_s','ur_oh_sls_s')})
if __name__=='__main__': main()
