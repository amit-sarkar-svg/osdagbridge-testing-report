import sys,inspect,textwrap
sys.path.insert(0,'/Users/macbook/Projects/OsdagBridge/src')
import osdagbridge.core.bridge_types.plate_girder.validator as V
from osdagbridge.core.utils.common import *
v=V.BridgeInputValidator()
for med in ("No","Yes","","None",None):
    print('BEFORE median=%r ->'%(med,), v.validate_basic_inputs(KEY_CARRIAGEWAY_WIDTH,{KEY_CARRIAGEWAY_WIDTH:None,KEY_INCLUDE_MEDIAN:med}))
src='class _X:\n'+inspect.getsource(V.BridgeInputValidator.validate_basic_inputs)
assert "if median else" in src
ns=dict(vars(V)); exec(src.replace("if median else","if median == 'Yes' else"),ns)
for med in ("No","Yes"):
    print('AFTER_FIX median=%r ->'%(med,), ns['_X'].validate_basic_inputs(v,KEY_CARRIAGEWAY_WIDTH,{KEY_CARRIAGEWAY_WIDTH:None,KEY_INCLUDE_MEDIAN:med}))
