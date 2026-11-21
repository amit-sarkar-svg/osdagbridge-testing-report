"""Cross-bracing design forces come from Vz_i of the transverse grillage members (crossbracingforces.py:326-358).
Compare |Vz_i| with |Vy_i| (vertical; ospgrillage loads act in y) in the same members, per load case.
usage: probe_bracing_vy_vz.py <params.json>"""
import sys,json,io,contextlib
sys.path.insert(0,'/Users/macbook/Projects/OsdagBridge/src'); sys.path.insert(0,'/Users/macbook/Projects/osdagbridge-testing-report/scripts')
def main():
    import design_runner as R
    from osdagbridge.core.bridge_types.plate_girder.plategirderbridge import PlateGirderBridge as P
    from osdagbridge.core.bridge_types.plate_girder.crossbracingforces import CrossBracingForces
    p=json.load(open(sys.argv[1])); b=P(); b.set_input(R.build(p)); buf=io.StringIO()
    with contextlib.redirect_stdout(buf): b.design()
    cb=CrossBracingForces(bridge=b); fd=cb.get_design_forces_dict()
    print('GEOM',fd.get('geometry')); print('BRACE',fd.get('brace_type'),'top',fd.get('top_chord'),'bottom',fd.get('bottom_chord'))
    for pr,v in fd['pairs'].items(): print('DESIGN_FORCE',pr,v)
    rd=b.result_data; F=rd['forces']; chains=rd.get('crossbracings',[])
    lcs=[lc for lc in F if lc in ('1.0 DL','1.0 LL','1.0 WL','WL Transverse','WL Uplift','DD','SW') or lc.startswith('BASIC_1')]
    for lc in lcs:
        mz=my=0; vz_at=vy_at=None
        for ch in chains:
            for m in ch.get('members',[]):
                f=F[lc].get(str(m)) or {}
                vz=abs(float(f.get('Vz_i',0) or 0)); vy=abs(float(f.get('Vy_i',0) or 0))
                if vz>mz: mz=vz
                if vy>my: my=vy
        print(f'LC {lc:45} max|Vz_i|={mz:10.2f}  max|Vy_i|={my:10.2f}   (units as stored)')
    print('N_CHAINS',len(chains))
if __name__=='__main__': main()
