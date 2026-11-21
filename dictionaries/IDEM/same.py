
import sys,json
sys.path.insert(0,"/Users/macbook/Projects/OsdagBridge/src")
from osdagbridge.core.bridge_types.plate_girder.plategirderbridge import PlateGirderBridge
d=json.load(open("/Users/macbook/Projects/osdagbridge-testing-report/test_cases/built/base.json"))
b=PlateGirderBridge(); b.set_input(d)
b.design(); o1=dict(b.output_dict)
b.design(); o2=dict(b.output_dict)
def sig(od):
 k=["geometry.span","typical_section.no_of_girders","steeldesign.details.moment.mu_applied","steeldesign.details.total_depth"]
 return {"core":[od.get(x) for x in k],"utils":{a:round(v,4) for a,v in od.items() if a.startswith("util.") and isinstance(v,(int,float))}}
print("IDEMPOTENCE", json.dumps({"run1":sig(o1),"run2":sig(o2),"equal":sig(o1)==sig(o2)}))
