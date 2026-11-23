"""SIDL (crash barrier / railing / median) never enters the DL combination.

create_sidl_combination() (analyser.py:1564) is defined but never called, so
self.sidl_combination stays None and create_dead_load_combination()
(analyser.py:1516, _DL_ATTRS at :1535) silently skips it. Every ULS/SLS
combination maps 'dead_load' -> 'dead_load_combination' (analyser.py:2319, :2517)
and the seismic mass uses the same case (:1040).

--fix : monkeypatch add_dead_loads to call create_sidl_combination() first.
usage: probe_sidl_missing.py <params.json> [--fix]
"""
import sys, json, io, contextlib
sys.path.insert(0, '/Users/macbook/Projects/OsdagBridge/src')
sys.path.insert(0, '/Users/macbook/Projects/osdagbridge-testing-report/scripts')


def main():
    import design_runner as R
    from osdagbridge.core.bridge_types.plate_girder.plategirderbridge import PlateGirderBridge as P
    fix = '--fix' in sys.argv
    if fix:
        orig = P.add_dead_loads
        def patched(self):
            gm = self.grillage_model
            real = gm.create_dead_load_combination
            def deferred(*a, **k):
                gm.create_sidl_combination()        # the missing call
                return real(*a, **k)
            gm.create_dead_load_combination = deferred
            try:
                return orig(self)
            finally:
                gm.create_dead_load_combination = real
        P.add_dead_loads = patched

    p = json.load(open(sys.argv[1])); b = P(); b.set_input(R.build(p))
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        b.design()
    gm = b.grillage_model
    print('MODE', 'FIXED' if fix else 'ORIGINAL', '| params', {k.split('.')[-1]: v for k, v in p.items()})
    print('sidl_combination is None:', getattr(gm, 'sidl_combination', None) is None)
    res = gm._load_case_resultant_kN
    for attr in ('self_weight_load_case', 'deck_load_case', 'footpath_load_case',
                 'crash_barrier_load_case', 'railing_load_case', 'median_load_case',
                 'sidl_combination', 'dead_load_combination'):
        lc = getattr(gm, attr, None)
        print(f'SUBCASE {attr:28} {"-" if lc is None else f"{res(lc):10.1f} kN"}')
    le = b._load_effects_cache
    g = max(le, key=lambda k: le[k]['1.0 DL']['Mz_max'])
    sel = ['SW', 'DD', '1.0 DW', 'Crash barrier load', '1.0 DL', '1.0 DL + 1.0 LL']
    print('GIRDER', g, {k: le[g][k]['Mz_max'] for k in sel if k in le[g]})
    s = le[g]
    comp = s['SW']['Mz_max'] + s['DD']['Mz_max']
    print(f'CHECK  1.0 DL ({s["1.0 DL"]["Mz_max"]}) - (SW+DD) ({round(comp,3)}) = {round(s["1.0 DL"]["Mz_max"]-comp,3)} kNm')
    dr = b.design_results
    print('DESIGN mu_applied', dr.get('Mu_kNm'), 'Vu', dr.get('Vu_kN'),
          'M_sls', dr.get('M_sls_kNm'), 'delta_total', dr.get('delta_total_mm'),
          'max_dcr', dr.get('max_dcr'), 'status', dr.get('overall_status'))
    for l in buf.getvalue().splitlines():
        if 'Seismic inputs' in l:
            print('LOG', l.strip()[:120])


if __name__ == '__main__':
    main()
