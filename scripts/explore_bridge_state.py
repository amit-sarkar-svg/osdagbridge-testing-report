"""Explore PlateGirderBridge attributes after design (span 20, cw 7.5, plain) to find reactions / load-case results."""
import sys,json
sys.path.insert(0,'/Users/macbook/Projects/OsdagBridge/src'); sys.path.insert(0,'/Users/macbook/Projects/osdagbridge-testing-report/scripts')
def main():
    import design_runner as R
    from osdagbridge.core.bridge_types.plate_girder.plategirderbridge import PlateGirderBridge as P
    p={"geometry.span":20.0,"geometry.carriageway_width":7.5,"geometry.skew_angle":0.0,"geometry.footpath":"None","geometry.include_median":"No","geometry.design_mode":"Optimized"}
    json.dump(p,open('test_cases/generated/H1_params.json','w'))
    b=P(); b.set_input(R.build(p)); b.design()
    for k,v in sorted(vars(b).items()):
        t=type(v).__name__; s=repr(v)[:70].replace('\n',' ')
        print('ATTR',k,t,len(v) if hasattr(v,'__len__') and not isinstance(v,str) else '',s)
if __name__=='__main__': main()
