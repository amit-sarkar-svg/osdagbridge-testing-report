"""Write report/sections/l4_counts.tex from evidence/xrun/l4_corners.jsonl."""
import json,collections
r=[json.loads(l) for l in open('evidence/xrun/l4_corners.jsonl')]
c=collections.Counter(x['status'] for x in r)
parts=[f"{v} {k}" for k,v in sorted(c.items())]
open('report/sections/l4_counts.tex','w').write(f"{len(r)} of 32 corner designs (span 20/45 m, carriageway min/23.6 m, skew $\\pm$15$^\\circ$, footpath, median): "+", ".join(parts).replace('_','\\_')+(" (timeouts are not yet conclusive, see Section~\\ref{sec:limits})" if c.get("timeout") else "")+"%\n")
print(len(r),dict(c))
