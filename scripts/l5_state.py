"""L5: sequences on ONE PlateGirderBridge using the UI path (set_input(copy of built dict); design()). Compares repeated A to first A and to a fresh object.
usage: l5_state.py <seq e.g. ABCA> -> evidence/xrun/l5_<seq>.json"""
import sys,json,time,copy,math,resource
sys.path.insert(0,'/Users/macbook/Projects/osdagbridge-testing-report/scripts')
import design_runner as R
from osdagbridge.core.bridge_types.plate_girder.plategirderbridge import PlateGirderBridge as P
PAR={'A':{"geometry.span":30.0,"geometry.carriageway_width":12.0,"geometry.skew_angle":0.0,"geometry.footpath":"None","geometry.include_median":"No","geometry.design_mode":"Optimized"},
     'B':{"geometry.span":25.0,"geometry.carriageway_width":8.0,"geometry.skew_angle":10.0,"geometry.footpath":"Single Side","geometry.include_median":"No","geometry.design_mode":"Optimized"},
     'C':{"geometry.span":40.0,"geometry.carriageway_width":15.0,"geometry.skew_angle":-5.0,"geometry.footpath":"None","geometry.include_median":"Yes","geometry.design_mode":"Optimized"}}
def main():
    seq=sys.argv[1]; built={k:R.build(v) for k,v in PAR.items()}
    def num(d): return {k:v for k,v in d.items() if isinstance(v,(int,float)) and not isinstance(v,bool)}
    def diff(a,b):
        a,b=num(a),num(b); bad=[]
        for k in set(a)|set(b):
            x,y=a.get(k),b.get(k)
            if x is None or y is None: bad.append((k,x,y)); continue
            if x!=y and not (isinstance(x,float) and isinstance(y,float) and (math.isnan(x) and math.isnan(y) or abs(x-y)<=1e-9*max(abs(x),abs(y),1))): bad.append((k,x,y))
        return bad
    b=P(); first={}; rec=[]
    for i,c in enumerate(seq):
        t=time.time(); b.set_input(copy.deepcopy(built[c]))
        try: b.design(); st='ok'; od=dict(b.output_dict)
        except Exception as e: st=f'EXC {type(e).__name__}: {str(e)[:80]}'; od={}
        r={'step':i,'case':c,'status':st,'s':round(time.time()-t,1),'rss_mb':round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1e6,0)}
        if c in first and od: bad=diff(first[c],od); r['diff_vs_first']=len(bad); r['diff_sample']=[(k,x,y) for k,x,y in bad[:4]]
        if c not in first and od: first[c]=od
        rec.append(r); print(r,flush=True)
    json.dump(rec,open(f'evidence/xrun/l5_{seq}.json','w'),indent=1,default=str)

if __name__ == '__main__':  # required: design() uses a multiprocessing forkserver pool
    main()
