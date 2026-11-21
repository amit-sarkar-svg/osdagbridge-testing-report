"""Fix proof (monkeypatch only): convert dims on a pristine copy each design()."""
import sys, json, copy
sys.path.insert(0,'/Users/macbook/Projects/osdagbridge-testing-report/scripts')
import design_runner as R
from osdagbridge.core.bridge_types.plate_girder.plategirderbridge import PlateGirderBridge as P
from osdagbridge.core.utils.common import KEY_MP_GIRDER_DEPTH
orig_design=P.design
def design_fixed(self):
    if not hasattr(self,'_pristine'): self._pristine=copy.deepcopy(self.input_dict)
    self.input_dict=copy.deepcopy(self._pristine)   # equivalent of "convert into a copy"
    return orig_design(self)
P.design=design_fixed
d=R.build(json.load(open('test_cases/generated/A1_params.json')))
b=P(); b.set_input(d)
out=[]
for i in (1,2):
    b.design(); out.append(b.input_dict[KEY_MP_GIRDER_DEPTH+'.G1.M1']); print(f'run{i} ok depth={out[-1]}')
print('same' if out[0]==out[1] else 'DIFF')
