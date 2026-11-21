"""Chart for the bracing-force finding: values copied from logs/probe_bracing_vy_vz.log and logs/probe_bracing_fix.log.
usage: make_chart.py <out.png>"""
import sys, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
lcs=['SW','DD','1.0 DL','1.0 LL','WL Transv.','BASIC_1']
vz=[0,0,0,0,0.35,0.35]; vy=[1.39,17.16,18.55,44.28,0,53.96]          # kN, max over bracing members
fig,ax=plt.subplots(1,2,figsize=(11,4.2))
x=range(len(lcs)); w=0.38
ax[0].bar([i-w/2 for i in x],vz,w,label='Vz (horizontal) - used by design',color='#c0392b')
ax[0].bar([i+w/2 for i in x],vy,w,label='Vy (vertical shear)',color='#2c7fb8')
ax[0].set_xticks(list(x)); ax[0].set_xticklabels(lcs,rotation=20); ax[0].set_ylabel('max force in bracing members (kN)')
ax[0].set_title('Force read by the bracing design is 0 for every gravity load'); ax[0].legend(fontsize=8); ax[0].grid(alpha=.3,axis='y')
ax[1].bar(['Current\n(Vz)','Docstring\n(vertical shear)'],[3.068,60.249],color=['#c0392b','#2c7fb8'])
ax[1].axhline(19.39,ls='--',color='k'); ax[1].text(0.5,21,'capacity of selected 40x40x3 strut = 19.39 kN',ha='center',fontsize=8)
ax[1].set_ylabel('governing diagonal compression (kN)'); ax[1].set_title('G1-G2 diagonal: design force'); ax[1].grid(alpha=.3,axis='y')
for i,v in enumerate([3.068,60.249]): ax[1].text(i,v+1,f'{v:.1f}',ha='center')
fig.suptitle('Cross-bracing design forces, span 20 m (same model, only the force component changed)'); fig.tight_layout(); fig.savefig(sys.argv[1],dpi=130)
