"""Fix proof for static-vehicle placement: wrap BridgeGrillageModel.vehicle_lane_coordinates so every static vehicle is
centred on the span (x offset = (L - vehicle length)/2) instead of starting at x=0; report governing LL and mu_applied.
usage: probe_vehicle_centered_fix.py <params.json> [--patch]"""
import sys,json,io,contextlib
sys.path.insert(0,'/Users/macbook/Projects/OsdagBridge/src'); sys.path.insert(0,'/Users/macbook/Projects/osdagbridge-testing-report/scripts')
def main():
    import design_runner as R
    from osdagbridge.core.bridge_types.plate_girder import analyser as A
    from osdagbridge.core.bridge_types.plate_girder.plategirderbridge import PlateGirderBridge as P
    from osdagbridge.core.utils.codes.irc6_2017 import IRC6_2017
    if '--patch' in sys.argv:
        vlen={'ClassA':max(IRC6_2017.cl_204_1_ClassA_vehicle()['x']),'Class70R':max(IRC6_2017.cl_204_1_Class70R_vehicle_wheel()['x'])}
        orig=A.BridgeGrillageModel.vehicle_lane_coordinates
        def centred(self,*a,**k):
            cases=orig(self,*a,**k)
            for c in cases:
                for vt,coords in c['combinations'].items():
                    off=max(0.0,(self.L-vlen.get(vt,0.0))/2.0)
                    c['combinations'][vt]=[(x+off,z) for x,z in coords]
            return cases
        A.BridgeGrillageModel.vehicle_lane_coordinates=centred
    p=json.load(open(sys.argv[1])); b=P(); b.set_input(R.build(p)); buf=io.StringIO()
    with contextlib.redirect_stdout(buf): b.design()
    for l in buf.getvalue().splitlines():
        if 'Governing LL:' in l: print('LOG',l.strip()[:150])
    od=b.output_dict; le=b._load_effects_cache
    print('PATCHED' if '--patch' in sys.argv else 'ORIGINAL', 'span',p['geometry.span'],'mu_applied',od.get('steeldesign.details.moment.mu_applied'),
          'LL_Mz per girder',{g:round(le[g]['1.0 DL + 1.0 LL']['Mz_max']-le[g]['1.0 DL']['Mz_max'],1) for g in le},
          'overall',b.design_results.get('overall_status'),'flexure dcr',[c['dcr'] for c in b.design_results['checks'] if c['name']=='ULS Flexure'])
if __name__=='__main__': main()
