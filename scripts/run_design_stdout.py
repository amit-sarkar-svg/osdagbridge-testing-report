"""Run one design and write the full design stdout to a file. usage: run_design_stdout.py <params.json> <out.log>"""
import sys,json,io,contextlib
sys.path.insert(0,'/Users/macbook/Projects/OsdagBridge/src'); sys.path.insert(0,'/Users/macbook/Projects/osdagbridge-testing-report/scripts')
def main():
    import design_runner as R
    from osdagbridge.core.bridge_types.plate_girder.plategirderbridge import PlateGirderBridge as P
    p=json.load(open(sys.argv[1])); b=P(); b.set_input(R.build(p)); buf=io.StringIO()
    with contextlib.redirect_stdout(buf): b.design()
    open(sys.argv[2],'w').write(buf.getvalue()); print('lines',len(buf.getvalue().splitlines()))
if __name__=='__main__': main()
