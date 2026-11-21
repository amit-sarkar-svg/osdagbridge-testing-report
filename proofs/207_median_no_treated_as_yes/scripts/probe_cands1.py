import sys
sys.path.insert(0,'/Users/macbook/Projects/OsdagBridge/src')
from osdagbridge.core.bridge_types.plate_girder.validator import BridgeInputValidator
from osdagbridge.core.utils.common import *
v=BridgeInputValidator()
def t(label,f):
    try: print(label,'->',repr(f()))
    except Exception as e: print(label,'EXC',type(e).__name__,e)
for x in (float('nan'),'nan',True,float('inf')):
    for k in (KEY_SPAN,KEY_SKEW_ANGLE,KEY_CARRIAGEWAY_WIDTH):
        t(f'{k} {x!r}',lambda:v.validate_basic_inputs(k,{k:x}))
t('cw None median No',lambda:v.validate_basic_inputs(KEY_CARRIAGEWAY_WIDTH,{KEY_CARRIAGEWAY_WIDTH:None,KEY_INCLUDE_MEDIAN:'No'}))
t('fy nan',lambda:v.validate_material_inputs(KEY_MATERIAL_GIRDER_FY,{KEY_MATERIAL_GIRDER_FY:float('nan')}))
for a,b in (("999","nan"),("inf","0"),("-500","1e999")):
    t(f'coords {a},{b}',lambda:v.validate_map_coordinates(a,b))
