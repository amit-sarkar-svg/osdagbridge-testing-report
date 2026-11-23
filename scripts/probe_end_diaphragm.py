"""Why are end-diaphragm designs empty on a cold run? Prints end_diaphragm_forces_dict, the support-edge element ->
girder-pair mapping used by _design_end_diaphragm_members (plategirderbridge.py:2590-2615) and the max |Vz|/|Vy|
in the end-edge members. usage: probe_end_diaphragm.py <params.json>"""
import sys,json,io,contextlib
sys.path.insert(0,'/Users/macbook/Projects/OsdagBridge/src'); sys.path.insert(0,'/Users/macbook/Projects/osdagbridge-testing-report/scripts')
def main():
    import design_runner as R
    from osdagbridge.core.bridge_types.plate_girder.plategirderbridge import PlateGirderBridge as P
    p=json.load(open(sys.argv[1])); b=P(); b.set_input(R.build(p)); buf=io.StringIO()
    with contextlib.redirect_stdout(buf): b.design()
    print('PARAMS',p)
    print('ED_FORCES',json.dumps(b.output_dict.get('end_diaphragm_forces_dict'),default=str)[:600])
    print('ED_DESIGNS',{k:(list(v) if isinstance(v,dict) else v) for k,v in (b.end_diaphragm_design_results or {}).items()})
    m=b.grillage_model.model; rd=b.result_data
    se=[str(e) for e in m.get_element(member="start_edge", options="elements")]; ee=[str(e) for e in m.get_element(member="end_edge", options="elements")]
    gs={g:set(d.get('nodes',[])) for g,d in rd.get('girders',{}).items()}
    def fg(n):
        for g,s in gs.items():
            if n in s: return g
    mapped={}; unm=0; notin=0
    for e in se+ee:
        if e not in rd.get('members',{}): notin+=1; continue
        n1,n2=rd['members'][e]; g1,g2=fg(n1),fg(n2)
        if g1 and g2 and g1!=g2: mapped.setdefault(f'{g1}-{g2}',[]).append(e)
        else: unm+=1
    print('EDGE_ELEMENTS start',len(se),'end',len(ee),'not_in_members',notin,'unmapped',unm,'mapped',{k:len(v) for k,v in mapped.items()})
    print('GIRDERS',list(gs), 'sample start_edge member nodes',[rd['members'].get(e) for e in se[:3]])
    F=rd['forces']; mx={}
    for lc in ('1.0 DL','1.0 LL','1.0 WL','WL Transverse'):
        if lc in F:
            vz=max((abs(float(F[lc].get(e,{}).get('Vz_i',0) or 0)) for e in se+ee),default=0); vy=max((abs(float(F[lc].get(e,{}).get('Vy_i',0) or 0)) for e in se+ee),default=0)
            print(f'LC {lc:15} end-edge max|Vz|={vz/1e3:.3f} kN  max|Vy|={vy/1e3:.3f} kN')
    for l in buf.getvalue().splitlines():
        if 'EndDiaphragm' in l: print('LOG',l[:140])
if __name__=='__main__': main()
