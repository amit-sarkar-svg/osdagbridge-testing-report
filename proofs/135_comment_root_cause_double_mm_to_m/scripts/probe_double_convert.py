"""Cand A1: does a 2nd design() on same object re-divide girder dims by 1000?"""
import sys, json, traceback
sys.path.insert(0,'/Users/macbook/Projects/osdagbridge-testing-report/scripts')
import design_runner as R
from osdagbridge.core.bridge_types.plate_girder.plategirderbridge import PlateGirderBridge
from osdagbridge.core.utils.common import KEY_MP_GIRDER_DEPTH, KEY_MP_GIRDER_WEB_DEPTH
d=R.build(json.load(open('test_cases/generated/A1_params.json')))
b=PlateGirderBridge(); b.set_input(d)
k=KEY_MP_GIRDER_DEPTH+'.G1.M1'
print('before', b.input_dict.get(k), b.input_dict.get(KEY_MP_GIRDER_DEPTH))
for i in (1,2):
    try: b.design(); print(f'run{i} ok')
    except Exception as e: print(f'run{i} EXC',type(e).__name__,str(e)[:100])
    print(f'after run{i}', b.input_dict.get(k), b.input_dict.get(KEY_MP_GIRDER_DEPTH), b.input_dict.get(KEY_MP_GIRDER_WEB_DEPTH))
