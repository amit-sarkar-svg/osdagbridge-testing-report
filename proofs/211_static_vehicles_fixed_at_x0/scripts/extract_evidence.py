"""Extract the live-load evidence for #211 from saved design states (<s12_dir>/<case>/state.json):
per-girder LL moment = Mz('1.0 DL + 1.0 LL') - Mz('1.0 DL'), plus mu_applied, for spans 20/30/40 m.
Writes span_series_extract.json and span_vs_ll_moment.png (program vs hand moving-load maximum,
hand values copied from logs/hand_moving_load.log). usage: extract_evidence.py <s12_dir> <out_dir>"""
import sys, json, os
HAND_70R_WORST = {20: 3320.1, 30: 5770.5, 40: 8222.0}      # logs/hand_fixed_vehicle.log, worst position
HAND_70R_AT_X0 = {20: 3304.6, 30: 4870.1, 40: 5823.8}      # logs/hand_fixed_vehicle.log, fixed at x = 0
def main():
    src, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True); rows = []
    for c in ['H_s20', 'H_s30', 'H_s40']:
        s = json.load(open(f'{src}/{c}/state.json')); le = s['_load_effects_cache']
        p = json.load(open(f'{src}/{c}/params.json')); od = s['output_dict']
        ll = {g: round(v['1.0 DL + 1.0 LL']['Mz_max'] - v['1.0 DL']['Mz_max'], 1) for g, v in le.items()}
        rows.append({'case': c, 'span_m': p['geometry.span'], 'LL_Mz_per_girder_kNm': ll,
                     'LL_Mz_sum_kNm': round(sum(ll.values()), 1),
                     'mu_applied_kNm': od.get('steeldesign.details.moment.mu_applied')})
        print(rows[-1])
    json.dump(rows, open(f'{out}/span_series_extract.json', 'w'), indent=1)
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    sp = [r['span_m'] for r in rows]; fig, ax = plt.subplots(1, 2, figsize=(10, 4))
    ax[0].plot(sp, [r['LL_Mz_sum_kNm'] for r in rows], 'o-', color='#c0392b')
    ax[0].set(title='Program: summed girder LL moment', xlabel='Span (m)', ylabel='kNm'); ax[0].grid(alpha=.3)
    ax[1].plot(sp, [HAND_70R_WORST[int(s)] for s in sp], 'o-', label='Worst position (correct)', color='#2c7fb8')
    ax[1].plot(sp, [HAND_70R_AT_X0[int(s)] for s in sp], 's--', label='Fixed at x = 0 (program)', color='#c0392b')
    ax[1].set(title='Hand calc: 70R on one simply supported line', xlabel='Span (m)', ylabel='kNm'); ax[1].legend(); ax[1].grid(alpha=.3)
    fig.suptitle('#211: live-load moment vs span (vehicles fixed at x = 0)'); fig.tight_layout()
    fig.savefig(f'{out}/span_vs_ll_moment.png', dpi=130); print('wrote', out)
if __name__ == '__main__': main()
