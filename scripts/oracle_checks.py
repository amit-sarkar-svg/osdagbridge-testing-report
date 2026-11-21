#!/usr/bin/env python3
"""Parse sweep results/logs and run metamorphic/oracle checks. No design runs here."""
from __future__ import annotations
import csv, json, re, math
from pathlib import Path
REPO=Path('/Users/macbook/Projects/osdagbridge-testing-report')

def parse_log(cid):
    p=REPO/'dictionaries'/cid/'case.log'
    if not p.exists(): return None
    t=p.read_text(errors='replace')
    out={'crash':False,'trace':[],'stage':'','dcr_rows':{},'verdict':'','max_dcr':None}
    m=re.search(r'Traceback \(most recent call last\):(.*?)(?=\n\S|\Z)', t, re.S)
    if m:
        out['crash']=True
        out['trace']=m.group(1).strip().splitlines()[-15:]
        # stage: look for STAGE or stage name near traceback
        sts=re.findall(r'STAGE\s+\S+|_run_stage\(.*?|Running stage \S+', t)
        out['stage']=sts[-1] if sts else '(unknown)'
    # DCR table lines: '#  Check ... DCR Status'
    for line in t.splitlines():
        mm=re.match(r'\s*\d+\s+(.+?)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+(PASS|WARN|\*FAIL\*|FAIL)', line)
        if mm:
            name=mm.group(1).strip(); dcr=float(mm.group(4)); status=mm.group(5).replace('*','').strip()
            out['dcr_rows'][name]=(dcr,status)
    vm=re.search(r'Status\s*:\s*(\w+)', t)
    if vm: out['verdict']=vm.group(1)
    mm=re.search(r'Maximum DCR\s*:\s*([\d.]+)', t)
    if mm: out['max_dcr']=float(mm.group(1))
    return out

def load_results():
    p=REPO/'test_cases'/'sweep_results.csv'
    if not p.exists(): return []
    return list(csv.DictReader(p.open()))

if __name__=='__main__':
    rows=load_results()
    print('sweep rows',len(rows))
    crashes=[]; completed=[]
    for r in rows:
        info=parse_log(r['id'])
        r['_info']=info
        if info and info['crash']: crashes.append(r)
        if r['status']=='ok': completed.append(r)
    print('crashes',len(crashes),'completed',len(completed))
    for r in crashes:
        print('CRASH',r['id'],'span',r['span'],'cw',r['cw'],'skew',r['skew'],'foot',r['foot'],'med',r['median'])
        print('  exc',r.get('exception','')[:90])
        print('  tail',crashes and r['_info']['trace'][-1][:100] if r['_info'] else '')
    # invariant: any DCR>1 reported as PASS?
    wrongpass=[]
    for r in completed:
        for name,(dcr,status) in (r['_info']['dcr_rows'] or {}).items():
            if dcr>=1.0 and status=='PASS': wrongpass.append((r['id'],name,dcr,status))
            if dcr<1.0 and status=='FAIL': wrongpass.append((r['id'],name,dcr,status))
    print('wrong PASS/FAIL count',len(wrongpass))
    for w in wrongpass[:10]: print('  ',w)
    (REPO/'evidence'/'logs'/'oracle_parsed.json').write_text(json.dumps({
      'rows':[{k:v for k,v in r.items() if k!='_info'} for r in rows],
      'crashes':[{'id':r['id'],'params':{k:r[k] for k in ['span','cw','skew','foot','median']},
                  'exc':r.get('exception',''),'trace':r['_info']['trace'],'stage':r['_info']['stage']} for r in crashes],
      'wrongpass':wrongpass}, indent=2))
    print('wrote oracle_parsed.json')
