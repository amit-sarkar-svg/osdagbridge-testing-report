"""Dead-load equilibrium oracle: applied SW/DD loads (from the design log and the load objects) vs
hand values (A*78.5*L per girder; slab t*25*deck area) and vs the girder moments in the load-effects cache.
usage: probe_dead_load_equilibrium.py <params.json>"""
import sys,json,io,contextlib
sys.path.insert(0,'/Users/macbook/Projects/OsdagBridge/src'); sys.path.insert(0,'/Users/macbook/Projects/osdagbridge-testing-report/scripts')
def main():
    import design_runner as R
    from osdagbridge.core.bridge_types.plate_girder.plategirderbridge import PlateGirderBridge as P
    p=json.load(open(sys.argv[1])); b=P(); b.set_input(R.build(p)); buf=io.StringIO()
    with contextlib.redirect_stdout(buf): b.design()
    for l in buf.getvalue().splitlines():
        if 'Self weight line load' in l or 'Deck slab load magnitude' in l: print('LOG',l.strip()[:150])
    gm=b.grillage_model; m=gm.model
    print('L',gm.L,'edge_dist',getattr(gm,'edge_dist',None))
    print('noz',[round(z,3) for z in m.Mesh_obj.noz])
    print('girder_props A (m2)',[round(g.A,6) for g in gm.girder_props])
    geo=gm.load_manager.deck_load(); print('deck patch', [(round(getattr(geo,k).x,3),round(getattr(geo,k).z,3)) for k in ('p1','p2','p3','p4')])
    for attr in ('girder_positions','girder_z','z_girders','girder_z_positions'):
        if hasattr(gm,attr): print(attr,getattr(gm,attr))
    le=b._load_effects_cache if hasattr(b,'_load_effects_cache') else None
    if le: print('cache girders',list(le), {g:(v['SW']['Mz_max'],v['DD']['Mz_max']) for g,v in le.items()})
if __name__=='__main__': main()
