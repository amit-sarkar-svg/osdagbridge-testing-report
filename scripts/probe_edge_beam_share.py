"""Edge-beam load share: the grillage gives the two deck-edge lines (where no girder exists) the full girder
section (plategirderbridge.py:1115). For SW / DD / LL, report max |Mz| per longitudinal member category
and the support reactions per transverse line; compare with statics (w L^2/8, total load).
usage: probe_edge_beam_share.py <params.json> [--soft-edge]   (--soft-edge: monkeypatch edge section to 1e-3 of the girder)"""
import sys,json,io,contextlib
sys.path.insert(0,'/Users/macbook/Projects/OsdagBridge/src'); sys.path.insert(0,'/Users/macbook/Projects/osdagbridge-testing-report/scripts')
def main():
    import design_runner as R
    from osdagbridge.core.bridge_types.plate_girder import plategirderbridge as PGB
    from osdagbridge.core.bridge_types.plate_girder.plategirderbridge import PlateGirderBridge as P
    if '--soft-edge' in sys.argv:
        orig=P.setup_grillage
        def patched(self):
            gs=self._girder_section
            def soft(i=None, _gs=gs):
                s=_gs(i)
                if i is None:
                    import dataclasses
                    return dataclasses.replace(s, A=s.A*1e-3, J=s.J*1e-3, Iz=s.Iz*1e-3, Iy=s.Iy*1e-3, Az=s.Az*1e-3, Ay=s.Ay*1e-3)
                return s
            self._girder_section=soft
            try: return orig(self)
            finally: del self._girder_section
        P.setup_grillage=patched
    p=json.load(open(sys.argv[1])); b=P(); b.set_input(R.build(p)); buf=io.StringIO()
    with contextlib.redirect_stdout(buf): b.design()
    gm=b.grillage_model; m=gm.model; ds=getattr(b,'_results_with_envelope',None) or getattr(gm,'_deduplicated_results',None)
    print('MODE','SOFT_EDGE' if '--soft-edge' in sys.argv else 'ORIGINAL','L',gm.L,'no_of_girders(input)',b.input_dict.get('typical_section.no_of_girders') if hasattr(b,'input_dict') else None)
    print('DATASET vars',list(ds.data_vars), 'dims', dict(ds.sizes))
    lcs=[str(x) for x in ds.coords['Loadcase'].values]
    ef=ds['forces_beam'] if 'forces_beam' in ds.data_vars else ds[[v for v in ds.data_vars if 'force' in v][0]]
    print('COMP',list(ef.coords['Component'].values)[:30]); print('LCS',lcs[:12])
    ec=ds['ele_nodes']; nc=ds['node_coordinates']
    zs={}
    for el in ds.coords['Element'].values:
        n=ec.sel(Element=el).values; a=nc.sel(Node=n[0]).values; c=nc.sel(Node=n[1]).values
        if abs(a[2]-c[2])<1e-6 and abs(a[0]-c[0])>1e-6: zs.setdefault(round(float(a[2]),3),[]).append(int(el))
    for cat,els in sorted(zs.items()):
        out={}
        for lc in [l for l in lcs if l in ('SW','DD','1.0 DW','LL') or l.startswith('1.0 LL') or l=='Crash barrier load'][:6]:
            v=ef.sel(Loadcase=lc, Element=els, Component=['Mz_i','Mz_j'])
            out[lc]=round(float(abs(v).max())/1000,1)
        print('CAT',cat,'n_el',len(els),out)
    print('LOG', [l.strip()[:110] for l in buf.getvalue().splitlines() if 'Self weight line load' in l][:1])
    od=b.output_dict; dr=b.design_results if isinstance(b.design_results,dict) else {}
    print('DESIGN mu_applied',od.get('steeldesign.details.moment.mu_applied'),'n_girders(design)',dr.get('n_girders'),'Mu',dr.get('Mu_kNm'),'Vu',dr.get('Vu_kN'),'overall',dr.get('overall_status'),'max_dcr',dr.get('max_dcr'))
    print('PER_GIRDER', {g:(v['demand'].get('Mu_kNm'),v['demand'].get('M_girder_sw_kNm')) for g,v in dr.get('per_girder',{}).items()})
if __name__=='__main__': main()
