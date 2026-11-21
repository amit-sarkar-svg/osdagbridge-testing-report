"""Lane sweep oracle: for each LW_* case, live-load effect = (1.0 DL + 1.0 LL) - (1.0 DL) on the governing girder,
plus mu_applied and live deflection. Live load must never be ~0 for a valid carriageway."""
import json,glob,os,re
def main():
    rows=[]
    for d in sorted(glob.glob('dictionaries/s12/LW_w*')+glob.glob('dictionaries/s12/MED_*')+glob.glob('dictionaries/s12/H_s*')):
        r=json.load(open(d+'/result.json'))
        if r['status']!='ok': rows.append((os.path.basename(d),r['status'])); continue
        s=json.load(open(d+'/state.json')); le=s['_load_effects_cache']; od=s['output_dict']; p=json.load(open(d+'/params.json'))
        ll=max((le[g].get('1.0 DL + 1.0 LL',{}).get('Mz_max',0) or 0)-(le[g].get('1.0 DL',{}).get('Mz_max',0) or 0) for g in le)
        n_lc=len(s['_lc_summary'] or {}); moving=[k for k in (s['_lc_summary'] or {}) if re.search(r'class|70r|veh|lane',k,re.I)]
        print(f"{os.path.basename(d):12} cw={p.get('geometry.carriageway_width'):5} span={p.get('geometry.span')} med={p.get('geometry.include_median')} "
              f"n_girders={s['design_results'].get('n_girders')} LL_Mz(max girder)={ll:8.2f} mu_applied={od.get('steeldesign.details.moment.mu_applied')} "
              f"delta_live={od.get('steeldesign.deflection.live_mm')} n_lc={n_lc} t={r['runtime_s']}")
if __name__=='__main__': main()
