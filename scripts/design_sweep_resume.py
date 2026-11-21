#!/usr/bin/env python3
"""Resume the 25-case sweep: skip completed, run remaining with 600s timeout, write CSV incrementally."""
from __future__ import annotations
import json, subprocess, sys, time, csv, os
from pathlib import Path
REPO=Path('/Users/macbook/Projects/osdagbridge-testing-report')
SCRIPTS=REPO/'scripts'; DICT=REPO/'dictionaries'
cases=json.load(open(REPO/'test_cases'/'sweep_cases.json'))
fields=['id','span','cw','skew','foot','median','status','runtime_s','exception','max_util','min_util']

def summarise(cid):
    outdir=DICT/cid
    rj=outdir/'result.json'
    status='no_result';runtime='';err=''
    if rj.exists():
        rr=json.loads(rj.read_text());status=rr.get('status','');runtime=rr.get('runtime_s','')
        _e=(rr.get('exception_type') or '');err=(_e.splitlines() or [_e])[0][:120] if _e else ''
    mx=mn=''
    oj=outdir/'output.json'
    if oj.exists():
        try:
            d=json.loads(oj.read_text())
            us=[float(v) for k,v in d.items() if k.startswith('util.') and isinstance(v,(int,float))]
            if us: mx=max(us);mn=min(us)
        except: pass
    return status,runtime,err,mx,mn

if __name__=='__main__':
    for c in cases:
        cid=c['id']; outdir=DICT/cid; outdir.mkdir(parents=True,exist_ok=True)
        if (outdir/'result.json').exists():
            print(cid,'SKIP already-done',flush=True); continue
        t0=time.time();status='no_result'
        try:
            with (outdir/'case.log').open('w') as log:
                subprocess.run([sys.executable,str(SCRIPTS/'design_runner.py'),'run',
                    str(REPO/'test_cases'/'built'/f'{cid}.input.json'),str(outdir)],
                    stdout=log,stderr=subprocess.STDOUT,timeout=600,
                    env={**os.environ,'QT_QPA_PLATFORM':'offscreen'})
        except subprocess.TimeoutExpired:
            status='timeout'
            (outdir/'result.json').write_text(json.dumps({'status':'timeout','exception_type':'','traceback':'','runtime_s':round(time.time()-t0,1)}))
            with (outdir/'case.log').open('a') as log: log.write('\n[resume] TIMEOUT 600s\n')
        st,runtime,err,mx,mn=summarise(cid)
        row=dict(id=cid,span=c['span'],cw=c['cw'],skew=c['skew'],foot=c['foot'],median=c['median'],
                 status=st or status,runtime_s=runtime,exception=err,max_util=mx,min_util=mn)
        # incremental CSV
        p=REPO/'test_cases'/'sweep_results.csv'
        exists=p.exists()
        with p.open('a',newline='') as f:
            w=csv.DictWriter(f,fieldnames=fields)
            if not exists: w.writeheader()
            w.writerow(row)
        print(cid,st or status,runtime,err[:50],flush=True)
    print('RESUME_DONE',flush=True)
