#!/usr/bin/env python3
"""Track L: 5 design runs on one object with reset() between, track wall time and RSS via resource."""
import sys,json,time,resource,os
sys.path.insert(0,'/Users/macbook/Projects/OsdagBridge/src')
from osdagbridge.core.bridge_types.plate_girder.plategirderbridge import PlateGirderBridge

def rss_mb():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024.0  # macOS bytes->KB->MB

if __name__=='__main__':
    d=json.load(open('/Users/macbook/Projects/osdagbridge-testing-report/test_cases/built/base.json'))
    b=PlateGirderBridge(); b.set_input(d)
    results=[]
    for i in range(5):
        if i>0: b.reset()
        t0=time.time()
        try:
            b.design()
            od=dict(b.output_dict)
            sig=(od.get('geometry.span'),od.get('steeldesign.details.moment.mu_applied'),
                 round({k:v for k,v in od.items() if k.startswith('util.')}.get('util.flexure',0),3))
            status='ok'
        except Exception as e:
            sig=None;status=f"{type(e).__name__}: {e}"
        dt=round(time.time()-t0,1)
        results.append({'run':i+1,'status':status,'wall_s':dt,'rss_mb':round(rss_mb(),1),'sig':sig})
        print(f"run{i+1} {status} wall={dt}s rss={rss_mb():.1f}MB sig={sig}",flush=True)
    sigs=[r['sig'] for r in results if r['status']=='ok']
    print('ALL_EQUAL',len(set(map(str,sigs)))==1 if sigs else 'n/a',flush=True)
    open('/Users/macbook/Projects/osdagbridge-testing-report/evidence/logs/trackL_stress.json','w').write(json.dumps(results,indent=2))
