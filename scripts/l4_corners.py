"""L4 corner sweep: each case = fresh subprocess (build, then design) with 600s timeout. JSONL -> evidence/xrun/l4_corners.jsonl"""
import itertools, json, subprocess, sys, time, resource
from pathlib import Path
R=Path(__file__).resolve().parent.parent; PY=sys.executable
out=R/'evidence/xrun/l4_corners.jsonl'; out.parent.mkdir(parents=True,exist_ok=True)
done=set()
if out.exists(): done={json.loads(l)['id'] for l in out.open()}
cases=[]
for span,cw,sk,fp,med in itertools.product((20,45),(4.25,23.6),(-15,15),("None","Both Sides"),("No","Yes")):
    if med=="Yes" and cw<7.5: cw=7.5
    cid=f"c_s{span}_w{cw}_k{sk}_{fp.replace(' ','')}_m{med}"
    cases.append((cid,{"geometry.span":float(span),"geometry.carriageway_width":cw,"geometry.skew_angle":float(sk),"geometry.footpath":fp,"geometry.include_median":med,"geometry.design_mode":"Optimized"}))
seen=set(); uniq=[]
for c in cases:
    if c[0] not in seen: seen.add(c[0]); uniq.append(c)
# hang-prone (#133) last
uniq.sort(key=lambda c:(c[1]["geometry.span"]==45 and c[1]["geometry.include_median"]=="Yes" and c[1]["geometry.footpath"]!="None"))
def lim(): resource.setrlimit(resource.RLIMIT_AS,(4<<30,4<<30)) if sys.platform!='darwin' else None
for cid,p in uniq:
    if cid in done: continue
    d=R/'dictionaries'/cid; d.mkdir(parents=True,exist_ok=True)
    pj=d/'params.json'; pj.write_text(json.dumps(p)); ij=d/'input.json'
    rec={"id":cid,"params":p,"status":"?"}
    t=time.time()
    try:
        b=subprocess.run([PY,str(R/'scripts/design_runner.py'),'build',str(pj),str(ij)],capture_output=True,text=True,timeout=120)
        if b.returncode: rec.update(status="build_fail",err=b.stderr[-300:])
        else:
            try:
                r=subprocess.run([PY,str(R/'scripts/design_runner.py'),'run',str(ij),str(d)],capture_output=True,text=True,timeout=600,preexec_fn=lim)
                res=json.loads((d/'result.json').read_text()); rec.update(status=res['status'],exc=res['exception_type'][:200],tb=res['traceback'][-400:])
            except subprocess.TimeoutExpired: rec.update(status="timeout")
    except subprocess.TimeoutExpired: rec.update(status="build_timeout")
    rec["wall_s"]=round(time.time()-t,1)
    with out.open('a') as f: f.write(json.dumps(rec)+"\n")
