#!/usr/bin/env python3
"""Generate pairwise-style 25-case subset and run design in subprocesses."""
from __future__ import annotations
import json, itertools, random, subprocess, sys, time, csv
from pathlib import Path

REPO = Path('/Users/macbook/Projects/osdagbridge-testing-report')
SCRIPTS = REPO/'scripts'; BUILT = REPO/'test_cases'/'built'; DICT = REPO/'dictionaries'
BUILT.mkdir(parents=True, exist_ok=True); DICT.mkdir(parents=True, exist_ok=True)

SPANS=[20.0,25.0,30.0,35.0,40.0,45.0]
CWS=[4.25,7.5,10.5,15.0,23.6]
SKEWS=[-15.0,-7.5,0.0,7.5,15.0]
FOOT=["None","Single Side","Both Sides"]
MED=["No","Yes"]

def valid(c):
    if c['median']=='Yes' and c['cw']<7.5: return False
    return True

def make_cases():
    # requirements: each param value, each (span,skew), each (cw,footpath)
    req=set()
    for s in SPANS: req.add(('span',s))
    for c in CWS: req.add(('cw',c))
    for s in SKEWS: req.add(('skew',s))
    for f in FOOT: req.add(('foot',f))
    for m in MED: req.add(('med',m))
    for s in SPANS:
        for k in SKEWS: req.add(('span_skew',s,k))
    for c in CWS:
        for f in FOOT: req.add(('cw_foot',c,f))
    cand=[]
    for s in SPANS:
        for c in CWS:
            for k in SKEWS:
                for f in FOOT:
                    for m in MED:
                        cc={'span':s,'cw':c,'skew':k,'foot':f,'median':m}
                        if valid(cc): cand.append(cc)
    def cover(c):
        x=set()
        x.add(('span',c['span'])); x.add(('cw',c['cw'])); x.add(('skew',c['skew']))
        x.add(('foot',c['foot'])); x.add(('med',c['median']))
        x.add(('span_skew',c['span'],c['skew'])); x.add(('cw_foot',c['cw'],c['foot']))
        return x
    covers=[cover(c) for c in cand]
    best_sol=None; best_uncov=999
    for seed in range(300):
        random.seed(seed)
        order=list(range(len(cand))); random.shuffle(order)
        chosen=[]; remaining=set(req); used=set()
        for idx in order:
            if len(chosen)>=25: break
            g=len(covers[idx]&remaining)
            if g>0:
                chosen.append(cand[idx]); remaining-=covers[idx]; used.add(idx)
        # try to fill remaining with best gains
        while remaining and len(chosen)<25:
            bi=None;bg=0
            for idx in range(len(cand)):
                if idx in used: continue
                g=len(covers[idx]&remaining)
                if g>bg: bg=g;bi=idx
            if bi is None: break
            chosen.append(cand[bi]); remaining-=covers[bi]; used.add(bi)
        if len(remaining)<best_uncov:
            best_uncov=len(remaining); best_sol=chosen
    return best_sol, len(req), best_uncov

def params_for(c):
    return {
      'geometry.span': c['span'], 'geometry.carriageway_width': c['cw'],
      'geometry.skew_angle': c['skew'], 'geometry.footpath': c['foot'],
      'geometry.include_median': c['median'], 'geometry.design_mode':'Optimized',
    }

if __name__=='__main__':
    cases, nreq, nrem = make_cases()
    print(f'cases={len(cases)} reqs={nreq} uncovered={nrem}')
    # write built inputs
    for i,c in enumerate(cases):
        cid=f'SW{i+1:02d}'
        pf=BUILT/f'{cid}.params.json'; pf.write_text(json.dumps(params_for(c)))
        inp=BUILT/f'{cid}.input.json'
        r=subprocess.run([sys.executable,str(SCRIPTS/'design_runner.py'),'build',str(pf),str(inp)],
                         capture_output=True,text=True)
        c['id']=cid; c['built']= r.returncode==0
    (REPO/'test_cases'/'sweep_cases.json').write_text(json.dumps(cases))
    # run designs
    rows=[]
    fields=['id','span','cw','skew','foot','median','status','runtime_s','exception','max_util','min_util']
    for c in cases:
        cid=c['id']; outdir=DICT/cid; outdir.mkdir(parents=True, exist_ok=True)
        t0=time.time(); status='no_result'; err=''; runtime=''
        try:
            with (outdir/'case.log').open('w') as log:
                pr=subprocess.run([sys.executable,str(SCRIPTS/'design_runner.py'),'run',
                                   str(BUILT/f'{cid}.input.json'),str(outdir)],
                                  stdout=log,stderr=subprocess.STDOUT,timeout=600,
                                  env={**__import__('os').environ,'QT_QPA_PLATFORM':'offscreen'})
            rj=outdir/'result.json'
            if rj.exists():
                rr=json.loads(rj.read_text()); status=rr['status']; runtime=rr.get('runtime_s','')
                _e=(rr.get('exception_type') or '')
                err=(_e.splitlines() or [_e])[0][:120] if _e else ''
        except subprocess.TimeoutExpired:
            status='timeout'; runtime=round(time.time()-t0,1)
        # extract util summary
        mx='';mn=''
        oj=outdir/'output.json'
        if oj.exists():
            try:
                d=json.loads(oj.read_text())
                us=[float(v) for k,v in d.items() if k.startswith('util.') and isinstance(v,(int,float))]
                if us: mx=max(us);mn=min(us)
            except: pass
        rows.append(dict(id=cid,span=c['span'],cw=c['cw'],skew=c['skew'],foot=c['foot'],median=c['median'],
                         status=status,runtime_s=runtime,exception=err,max_util=mx,min_util=mn))
        print(cid,status,runtime,err[:60],flush=True)
    with (REPO/'test_cases'/'sweep_results.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
    print('DONE', len(rows))
