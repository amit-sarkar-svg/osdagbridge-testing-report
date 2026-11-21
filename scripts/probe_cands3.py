import sys
sys.path.insert(0,'/Users/macbook/Projects/OsdagBridge/src')
from osdagbridge.core.bridge_types.plate_girder.plategirderbridge import PlateGirderBridge as P
b=P()
for args in (("E 999","Yield Strength"),("","Yield Strength"),("E 250","Yield Strength"),("E 250","Bogus Property")):
    try: print('lookup',args,'->',repr(b._lookup_material(*args)))
    except Exception as e: print('lookup',args,'EXC',type(e).__name__,str(e)[:90])
