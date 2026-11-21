"""Run design cases one per fresh subprocess; save output_dict + internal summaries (reactions, load effects, deflections, design/deck results).
usage: batch_design.py <cases.json> <out_dir>      cases.json = {"ID": {params...}, ...}
Each case: <out_dir>/<ID>/{params.json,input.json,state.json,result.json}. Resumable (skips cases with result.json)."""
import sys,json,time,subprocess,os
from pathlib import Path
R=Path(__file__).resolve().parent.parent
CHILD=r'''
import sys,json,time,traceback
sys.path.insert(0,'/Users/macbook/Projects/OsdagBridge/src'); sys.path.insert(0,'/Users/macbook/Projects/osdagbridge-testing-report/scripts')
def main():
    import design_runner as R
    from osdagbridge.core.bridge_types.plate_girder.plategirderbridge import PlateGirderBridge as P
    d=sys.argv[1]; p=json.load(open(d+'/params.json')); res={'status':'ok'}; t=time.time()
    try:
        inp=R.build(p); json.dump(R.jsonable(inp),open(d+'/input.json','w'))
        b=P(); b.set_input(inp); b.design()
        st={'output_dict':dict(b.output_dict)}
        for a in ('_reaction_summary','_lc_summary','_load_effects_cache','_deflections_cache','design_results','deck_design_results'):
            st[a]=getattr(b,a,None)
        st['grillage_geometry']=repr(getattr(b,'grillage_geometry',None)); st['material_props']=repr(getattr(b,'material_props',None)); st['deck_layout']=repr(getattr(b,'deck_layout',None))
        json.dump(R.jsonable(st),open(d+'/state.json','w'))
    except Exception as e:
        res={'status':'exception','exc':f'{type(e).__name__}: {e}'[:300],'tb':traceback.format_exc()[-1500:]}
    res['runtime_s']=round(time.time()-t,1); json.dump(res,open(d+'/result.json','w')); print(res['status'],res.get('exc',''),res['runtime_s'])
if __name__=='__main__': main()
'''
def main():
    cases=json.load(open(sys.argv[1])); out=Path(sys.argv[2]); out.mkdir(parents=True,exist_ok=True)
    child=out/'_child.py'; child.write_text(CHILD)
    for cid,p in cases.items():
        d=out/cid; d.mkdir(exist_ok=True)
        if (d/'result.json').exists(): continue
        (d/'params.json').write_text(json.dumps(p))
        t=time.time()
        try:
            r=subprocess.run([sys.executable,str(child),str(d)],capture_output=True,text=True,timeout=600)
            (d/'stderr_tail.log').write_text(r.stderr[-4000:])
        except subprocess.TimeoutExpired:
            (d/'result.json').write_text(json.dumps({'status':'timeout','runtime_s':600}))
        print(cid,json.loads((d/'result.json').read_text()).get('status'),round(time.time()-t,1),flush=True)
if __name__=='__main__': main()
