#!/usr/bin/env python3
"""Controlled single-variable / metamorphic design runs (built from defaults)."""
from __future__ import annotations
import json, subprocess, sys, time, os
from pathlib import Path
REPO=Path('/Users/macbook/Projects/osdagbridge-testing-report')
SCRIPTS=REPO/'scripts'; BUILT=REPO/'test_cases'/'built'; DICT=REPO/'dictionaries'
BUILT.mkdir(parents=True,exist_ok=True)

BASE={'geometry.span':30.0,'geometry.carriageway_width':10.5,'geometry.skew_angle':0.0,
      'geometry.footpath':'None','geometry.include_median':'No','geometry.design_mode':'Optimized'}

CASES={
 'OR_SPAN30': {},
 'OR_SPAN45': {'geometry.span':45.0},
 'OR_CW75':   {'geometry.carriageway_width':7.5},
 'OR_CW150':  {'geometry.carriageway_width':15.0},
 'OR_SKEW0':  {},                      # same as OR_SPAN30
 'OR_SKEW15': {'geometry.skew_angle':15.0},
 'OR_SKEWM15':{'geometry.skew_angle':-15.0},
 'OR_SKEW75': {'geometry.skew_angle':7.5},
 'OR_SKEWM75':{'geometry.skew_angle':-7.5},
 'OR_FOOT':   {'geometry.footpath':'Both Sides'},
 'OR_MED':    {'geometry.include_median':'Yes','geometry.carriageway_width':10.5},
}

def build(cid,over):
    p={**BASE,**over}; pf=BUILT/f'{cid}.params.json'; inf=BUILT/f'{cid}.input.json'
    pf.write_text(json.dumps(p))
    subprocess.run([sys.executable,str(SCRIPTS/'design_runner.py'),'build',str(pf),str(inf)],
                   capture_output=True,text=True,check=True)
    return inf

if __name__=='__main__':
    sel=sys.argv[1:] or list(CASES)
    for cid in sel:
        inf=build(cid,CASES[cid]); outdir=DICT/cid; outdir.mkdir(parents=True,exist_ok=True)
        t0=time.time()
        try:
            with (outdir/'case.log').open('w') as log:
                subprocess.run([sys.executable,str(SCRIPTS/'design_runner.py'),'run',str(inf),str(outdir)],
                               stdout=log,stderr=subprocess.STDOUT,timeout=600,
                               env={**os.environ,'QT_QPA_PLATFORM':'offscreen'})
        except subprocess.TimeoutExpired:
            print(cid,'TIMEOUT',flush=True); continue
        rj=outdir/'result.json'
        rr=json.loads(rj.read_text()) if rj.exists() else {}
        print(cid,rr.get('status'),rr.get('runtime_s',round(time.time()-t0,1)),rr.get('exception_type','')[:60],flush=True)
