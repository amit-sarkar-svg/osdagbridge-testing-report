import sys,json
sys.path.insert(0,"/Users/macbook/Projects/OsdagBridge/src")
from osdagbridge.core.bridge_types.plate_girder.plategirderbridge import PlateGirderBridge
def sig(od):
    k=["geometry.span","typical_section.no_of_girders","steeldesign.details.moment.mu_applied","steeldesign.details.total_depth"]
    return {"core":[od.get(x) for x in k],"utils":{a:round(v,4) for a,v in od.items() if a.startswith("util.") and isinstance(v,(int,float))}}
if __name__ == "__main__":
    d=json.load(open("/Users/macbook/Projects/osdagbridge-testing-report/test_cases/built/base.json"))
    b=PlateGirderBridge(); b.set_input(d)
    b.design(); o1=sig(dict(b.output_dict)); print("RUN1_DONE",flush=True)
    b.design(); o2=sig(dict(b.output_dict)); print("RUN2_DONE",flush=True)
    print("IDEMPOTENCE " + json.dumps({"equal":o1==o2,"run1":o1,"run2":o2}),flush=True)
