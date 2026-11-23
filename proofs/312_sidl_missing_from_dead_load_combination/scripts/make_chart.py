"""Chart for the SIDL finding. Values from logs/probe_sidl_missing.log and logs/probe_sidl_fp_med.log.
usage: make_chart.py <out.png>"""
import sys, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
names = ['self weight', 'deck slab', 'footpath', 'crash barrier', 'railing', 'median']
applied = [220.3, 2618.8, 294.3, 261.6, 58.9, 80.0]            # span 20, footpath both + median
in_dl   = [220.3, 2618.8, 294.3, 0.0, 0.0, 0.0]
x = range(len(names)); w = 0.38
ax[0].bar([i - w/2 for i in x], applied, w, label='applied to the grillage', color='#2c7fb8')
ax[0].bar([i + w/2 for i in x], in_dl, w, label='reaches the DL combination', color='#c0392b')
ax[0].set_xticks(list(x)); ax[0].set_xticklabels(names, rotation=20, ha='right')
ax[0].set_ylabel('load resultant (kN)'); ax[0].legend(fontsize=8); ax[0].grid(alpha=.3, axis='y')
ax[0].set_title('400.5 kN of SIDL applied but never combined', fontsize=10)
labels = ['Moment\n(kNm)', 'Shear\n(kN)', 'LTB constr.\n(kNm)', 'Deflection\n(mm)', 'Fatigue\n(MPa)']
shipped = [1141.82, 250.02, 483.35, 21.52, 204.28]
fixed   = [1211.25, 266.17, 552.96, 22.96, 217.26]
x2 = range(len(labels))
ax[1].bar([i - w/2 for i in x2], shipped, w, label='as shipped', color='#c0392b')
ax[1].bar([i + w/2 for i in x2], fixed, w, label='with SIDL in DL', color='#2c7fb8')
ax[1].set_xticks(list(x2)); ax[1].set_xticklabels(labels, fontsize=8)
ax[1].set_yscale('log'); ax[1].set_ylabel('girder demand (log scale)')
ax[1].legend(fontsize=8); ax[1].grid(alpha=.3, axis='y')
for i, (a, b) in enumerate(zip(shipped, fixed)):
    ax[1].text(i, max(a, b) * 1.15, f'+{(b/a-1)*100:.1f}%', ha='center', fontsize=8)
ax[1].set_ylim(top=max(fixed)*2.2)
ax[1].set_title('Girder demands under-stated (span 20 m)', fontsize=10)
fig.suptitle('SIDL (crash barrier / railing / median) never enters the DL combination')
fig.tight_layout(); fig.savefig(sys.argv[1], dpi=130)
