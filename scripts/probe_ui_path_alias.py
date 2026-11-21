"""UI path: template_page does backend.set_input(input_dict); backend.design() on the SAME UI dict each press."""
import sys, json
sys.path.insert(0,'/Users/macbook/Projects/osdagbridge-testing-report/scripts')
import design_runner as R
from osdagbridge.core.bridge_types.plate_girder.plategirderbridge import PlateGirderBridge as P
from osdagbridge.core.utils.common import KEY_MP_GIRDER_DEPTH
d=R.build(json.load(open('test_cases/generated/A1_params.json')))
k=KEY_MP_GIRDER_DEPTH+'.G1.M1'
b=P()
for i in (1,2):
    b.set_input(d)
    try: b.design(); print(f'press{i} ok')
    except Exception as e: print(f'press{i} EXC',type(e).__name__,e)
    print(f'  ui_dict[{k}]={d.get(k)}  backend={b.input_dict.get(k)}  aliased={b.input_dict is d}')
