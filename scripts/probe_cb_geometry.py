"""Capture crash-barrier/median line-load geometry printed by the analyser for a plain span-20 bridge (H1 params)."""
import sys,json,io,contextlib
sys.path.insert(0,'/Users/macbook/Projects/OsdagBridge/src'); sys.path.insert(0,'/Users/macbook/Projects/osdagbridge-testing-report/scripts')
def main():
    import design_runner as R
    from osdagbridge.core.bridge_types.plate_girder.plategirderbridge import PlateGirderBridge as P
    p=json.load(open(sys.argv[1])); b=P(); b.set_input(R.build(p))
    buf=io.StringIO()
    with contextlib.redirect_stdout(buf):
        b.design()
    for l in buf.getvalue().splitlines():
        if any(t in l for t in ('Crash barrier','crash barrier','Median','median line','DW','wearing','Deck dead','line load: start')): print('LOG',l[:200])
    lm=b.grillage_model.load_manager if hasattr(b.grillage_model,'load_manager') else None
    print('LOAD_MANAGER',type(lm).__name__)
if __name__=='__main__': main()
