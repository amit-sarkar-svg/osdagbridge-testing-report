import sys, json, copy
sys.path.insert(0,'/Users/macbook/Projects/OsdagBridge/src'); sys.path.insert(0,'/Users/macbook/Projects/osdagbridge-testing-report/scripts')
from osdagbridge.core.bridge_types.plate_girder.defaults import BASIC_INPUT_DICT, solve_extend_basic_input_dict as S
from osdagbridge.core.utils.common import *
base={"geometry.span":30.0,"geometry.carriageway_width":12.0,"geometry.skew_angle":0.0,"geometry.footpath":"None","geometry.include_median":"No"}
def run(label,**kw):
    d=dict(BASIC_INPUT_DICT); d.update(base); d.update(kw)
    try: S(d); return d
    except Exception as e: print(label,'EXC',type(e).__name__,str(e)[:100]); return None
d=run('ref')
print('ref n,spacing,overhang',d.get(KEY_TS_NO_OF_GIRDERS),d.get(KEY_TS_GIRDER_SPACING),d.get(KEY_TS_DECK_OVERHANG), 'width', d.get(KEY_TS_DECK_WIDTH) if 'KEY_TS_DECK_WIDTH' in dir() else '')
# C06: user-supplied spacing/overhang preserved?
d=run('C06',**{KEY_TS_NO_OF_GIRDERS:4,KEY_TS_GIRDER_SPACING:2.5,KEY_TS_DECK_OVERHANG:0.9})
if d: print('C06 entered spacing 2.5 overhang 0.9 n=4 ->',d.get(KEY_TS_GIRDER_SPACING),d.get(KEY_TS_DECK_OVERHANG))
# C07/C-median: width
for med,mw in (("No",0),("Yes",1.0)):
    d=run('med',**{"geometry.include_median":med,"geometry.carriageway_width":8.0,**({KEY_TS_MEDIAN_WIDTH:mw} if 'KEY_TS_MEDIAN_WIDTH' in dir() else {})})
    if d: print('median',med,'->',{k:v for k,v in d.items() if 'width' in k.lower() and not isinstance(v,(dict,list))})
# girder count parse
for nv in ("3.0","0",3.0,"4"):
    d=run('n',**{KEY_TS_NO_OF_GIRDERS:nv})
    if d: print('n_girders input',repr(nv),'->',d.get(KEY_TS_NO_OF_GIRDERS))
# C08 None carriageway
run('C08',**{"geometry.carriageway_width":None})
# input mutated for unrelated keys?
d0=dict(BASIC_INPUT_DICT); d0.update(base); s0=copy.deepcopy(d0); S(d0)
print('keys changed by solver:',sorted(k for k in s0 if k in d0 and s0[k]!=d0[k])[:12])
