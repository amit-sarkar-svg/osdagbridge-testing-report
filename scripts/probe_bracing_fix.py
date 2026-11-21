"""Cross-bracing design forces with the component the docstring describes ("Chord force equals the full
vertical shear", crossbracingforces.py header Step 4) vs the component actually read (Vz_i, horizontal).
--vy: monkeypatch CrossBracingForces._read_vz to return Vy_i/Vy_j (vertical shear) instead of Vz_i/Vz_j.
Prints the design forces per pair and the selected sections, capacities and efficiencies.
usage: probe_bracing_fix.py <params.json> [--vy]"""
import sys,json,io,contextlib
sys.path.insert(0,'/Users/macbook/Projects/OsdagBridge/src'); sys.path.insert(0,'/Users/macbook/Projects/osdagbridge-testing-report/scripts')
def main():
    import design_runner as R
    from osdagbridge.core.bridge_types.plate_girder.plategirderbridge import PlateGirderBridge as P
    from osdagbridge.core.bridge_types.plate_girder import crossbracingforces as CBF
    if '--vy' in sys.argv:
        def read_vy(self, lc, member_id, is_i):
            comp = "Vy_i" if is_i else "Vy_j"
            try: return float(self.bridge.result_data["forces"][str(lc)][member_id][comp])
            except (KeyError, TypeError, ValueError): return None
        CBF.CrossBracingForces._read_vz = read_vy
    p=json.load(open(sys.argv[1])); b=P(); b.set_input(R.build(p)); buf=io.StringIO()
    with contextlib.redirect_stdout(buf): b.design()
    print('MODE','VY (docstring: vertical shear)' if '--vy' in sys.argv else 'ORIGINAL (Vz, horizontal)')
    fd=b.output_dict.get('crossbracing_forces_dict') or {}
    for pr,v in (fd.get('pairs') or {}).items():
        print('FORCE',pr,'diagT',v.get('diag_tension_kN'),v.get('diag_tension_gov_lc'),'| diagC',v.get('diag_compression_kN'),v.get('diag_compression_gov_lc'))
    pd=b.crossbracing_design_results or {}
    for pr,mem in pd.items():
        for mname,ft in (mem or {}).items():
            for t,res in (ft or {}).items():
                if not isinstance(res,dict): continue
                flat={}
                def f(o,p=''):
                    if isinstance(o,dict):
                        for k,v in o.items(): f(v,p+'.'+str(k))
                    else: flat[p[1:]]=o
                f(res)
                pick={k:flat[k] for k in flat if any(s in k for s in ('designation','tension_capacity','efficiency','KEY_FCD','Slenderness'))}
                print('DESIGN',pr,mname,t,{k.split('.')[-1] if 'designation' not in k else 'section':v for k,v in pick.items()})
if __name__=='__main__': main()
