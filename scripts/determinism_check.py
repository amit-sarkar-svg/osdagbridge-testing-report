#!/usr/bin/env python3
"""Determinism/idempotence with proper __main__ guard (avoid multiprocessing re-exec)."""
import sys,json,subprocess,os
from pathlib import Path
REPO=Path('/Users/macbook/Projects/osdagbridge-testing-report')
DICT=REPO/'dictionaries'; INP=REPO/'test_cases'/'built'/'base.json'

same_script = '''import sys,json
sys.path.insert(0,"/Users/macbook/Projects/OsdagBridge/src")
from osdagbridge.core.bridge_types.plate_girder.plategirderbridge import PlateGirderBridge
def sig(od):
    k=["geometry.span","typical_section.no_of_girders","steeldesign.details.moment.mu_applied","steeldesign.details.total_depth"]
    return {"core":[od.get(x) for x in k],"utils":{a:round(v,4) for a,v in od.items() if a.startswith("util.") and isinstance(v,(int,float))}}
if __name__ == "__main__":
    d=json.load(open("''' + str(INP) + '''"))
    b=PlateGirderBridge(); b.set_input(d)
    b.design(); o1=sig(dict(b.output_dict)); print("RUN1_DONE",flush=True)
    b.design(); o2=sig(dict(b.output_dict)); print("RUN2_DONE",flush=True)
    print("IDEMPOTENCE " + json.dumps({"equal":o1==o2,"run1":o1,"run2":o2}),flush=True)
'''

if __name__ == "__main__":
    out=DICT/'IDEM2';out.mkdir(parents=True,exist_ok=True)
    (out/'same.py').write_text(same_script)
    env={**os.environ,'QT_QPA_PLATFORM':'offscreen'}
    with (out/'same.log').open('w') as log:
        pr=subprocess.run([sys.executable,str(out/'same.py')],stdout=log,stderr=subprocess.STDOUT,timeout=600,env=env)
    txt=(out/'same.log').read_text()
    print('EXIT',pr.returncode)
    for line in txt.splitlines():
        if 'RUN1_DONE' in line or 'RUN2_DONE' in line or 'IDEMPOTENCE' in line or 'ValueError' in line or 'Traceback' in line:
            print(line[:400])
