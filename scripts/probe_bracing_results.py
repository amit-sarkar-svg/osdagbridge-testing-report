"""Run design and dump cross-bracing / end-diaphragm design results (flattened). usage: probe_bracing_results.py <params.json> <out.json>"""
import sys,json,io,contextlib
sys.path.insert(0,'/Users/macbook/Projects/OsdagBridge/src'); sys.path.insert(0,'/Users/macbook/Projects/osdagbridge-testing-report/scripts')
def flat(o,p='',out=None):
    out={} if out is None else out
    if isinstance(o,dict):
        for k,v in o.items(): flat(v,f'{p}.{k}' if p else str(k),out)
    elif isinstance(o,(list,tuple)) and o and isinstance(o[0],(dict,list,tuple)):
        for i,v in enumerate(o): flat(v,f'{p}[{i}]',out)
    elif hasattr(o,'__dict__') and not isinstance(o,type):
        flat(vars(o),p,out)
    else: out[p]=o if isinstance(o,(int,float,str,bool,type(None))) else str(o)[:120]
    return out
def main():
    import design_runner as R
    from osdagbridge.core.bridge_types.plate_girder.plategirderbridge import PlateGirderBridge as P
    p=json.load(open(sys.argv[1])); b=P(); b.set_input(R.build(p)); buf=io.StringIO()
    with contextlib.redirect_stdout(buf): b.design()
    out={'cb':flat(getattr(b,'crossbracing_design_results',None)),'ed':flat(getattr(b,'end_diaphragm_design_results',None)),
         'od_cb':{k:v for k,v in b.output_dict.items() if ('bracing' in k or 'diaphragm' in k) and not isinstance(v,(dict,list))}}
    json.dump(out,open(sys.argv[2],'w'),indent=0,default=str); print('cb keys',len(out['cb']),'ed keys',len(out['ed']),'od',len(out['od_cb']))
    open(sys.argv[2]+'.log','w').write(buf.getvalue())
if __name__=='__main__': main()
