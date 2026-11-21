"""Oracle over dictionaries/c_*/output.json: finite, non-negative dims, ratios sane. Prints violations per case."""
import json,glob,re,math,sys,collections
DIM=re.compile(r'(width|depth|thickness|spacing|mass|span|length|area)(\.|$|_)',re.I)
out=collections.defaultdict(list)
for f in sorted(glob.glob('dictionaries/c_*/output.json')):
    cid=f.split('/')[1]
    try: d=json.load(open(f))
    except Exception as e: out[cid].append(('unreadable',str(e)[:50])); continue
    for k,v in d.items():
        if isinstance(v,str) and v.strip().lower() in ('nan','inf','-inf'): out[cid].append(('nonfinite',k,v))
        elif isinstance(v,(int,float)) and not isinstance(v,bool):
            if DIM.search(k) and v<0: out[cid].append(('negative_dim',k,v))
            if re.search(r'chi_lt$',k) and not (0<v<=1.0001): out[cid].append(('chi_lt_range',k,v))
            if re.search(r'(mn_ratio|_ratio|dcr)$',k) and v<0: out[cid].append(('neg_ratio',k,v))
n=len(glob.glob('dictionaries/c_*/output.json')); print('cases checked',n,'with violations',len(out))
for c,v in list(out.items())[:15]: print(c,collections.Counter(x[0] for x in v),v[:2])
