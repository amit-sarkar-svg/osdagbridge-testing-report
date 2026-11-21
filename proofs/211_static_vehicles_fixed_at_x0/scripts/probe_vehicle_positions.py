"""After design, dump global positions of every point load in every static vehicle load case and the governing LL case.
usage: probe_vehicle_positions.py <params.json>"""
import sys,json,io,contextlib,re
sys.path.insert(0,'/Users/macbook/Projects/OsdagBridge/src'); sys.path.insert(0,'/Users/macbook/Projects/osdagbridge-testing-report/scripts')
def pts(obj):
    out=[]
    for v in vars(obj).values():
        if hasattr(v,'_fields') and {'x','z','p'}<=set(v._fields) and v.p is not None: out.append((round(v.x,3),round(v.z,3),round(v.p/1000,2)))
    return out
def main():
    import design_runner as R
    from osdagbridge.core.bridge_types.plate_girder.plategirderbridge import PlateGirderBridge as P
    p=json.load(open(sys.argv[1])); b=P(); b.set_input(R.build(p)); buf=io.StringIO()
    with contextlib.redirect_stdout(buf): b.design()
    for l in buf.getvalue().splitlines():
        if 'Governing LL' in l or 'impact' in l.lower() or 'dla' in l.lower(): print('LOG',l.strip()[:150])
    gm=b.grillage_model; print('SPAN',getattr(gm,'L',None))
    for lc in getattr(gm,'vehicle_load_cases_list',[]):
        allp=[]
        for g in lc.load_groups:
            ld=g['load']; f=g.get('load_factor',1)
            for sub in getattr(ld,'compound_load_obj_list',[ld]): allp+= [(x,z,pp,f) for x,z,pp in pts(sub)]
        xs=sorted({a[0] for a in allp})
        print(f'CASE {lc.name[:40]:40} n_pts={len(allp):3} x_range=[{min(xs) if xs else None}, {max(xs) if xs else None}] total_kN={sum(a[2] for a in allp):.1f}')
if __name__=='__main__': main()
