#!/usr/bin/env python3
"""Additional calc checks: crack-control, stud capacity, scaling, gamma values, comparison direction."""
import sys, math
sys.path.insert(0,'/Users/macbook/Projects/OsdagBridge/src')
from osdagbridge.core.bridge_types.plate_girder import deckdesign as D
from osdagbridge.core.utils.codes.irc22_2015 import IRC22_2014 as I
from osdagbridge.core.utils.codes.is800_2007 import IS800_2007 as S
from osdagbridge.core.utils.codes import keyfile as K

def show(label, exp, act, tol=0.01):
    m = (abs(exp-act)<=tol) if isinstance(exp,(int,float)) and isinstance(act,(int,float)) else (exp==act)
    print(f"{label:38s} exp={str(exp)[:20]:20s} act={str(act)[:22]:22s} match={m}")

# 1 crack-control: IRC22 604.4 docstring: As_top>=kc*k*fctm*t_slab*1000/fy; kc=0.5,k=0.65
fctm,fy,ts=2.5,500,200
exp=0.5*0.65*fctm*ts*1000/fy
act=D._crack_control_min_top_steel_mm2_per_m(fctm,fy,ts)
show('crack_control As_min', round(exp,3), round(act,3))
# scaling: double fctm -> double As
act2=D._crack_control_min_top_steel_mm2_per_m(2*fctm,fy,ts)
show('crack_control As_min 2x fctm -> 2x', round(2*act,3), round(act2,3))

# 2 stud steel strength Eq6.1: Qu_steel = 0.8*fu*pi*d^2/4/gamma_v ; N
d,hs,fu,gv=20,100,500,1.25
exp_qs=0.8*fu*math.pi*d**2/4/gv
r=I.cl_606_3_1_stud_connector_strength(d,hs,fu_MPa=fu,fck_cu_MPa=30,Ecm_MPa=30000,gamma_v=gv)
print('stud full keys sample',list(r.keys())[:12])
qs=r.get('Qu_steel_kN')
show('stud Qu_steel Eq6.1 (kN)', round(exp_qs/1000,3), round(qs,3) if qs else qs)
# govern with very high fu -> concrete governs; check Qu is min
qmin=min([v for k,v in r.items() if k.startswith('Qu') and isinstance(v,(int,float)) and v>0]) if any(k.startswith('Qu') for k in r) else None
print('stud all Qu keys',{k:v for k,v in r.items() if k.startswith('Qu') and isinstance(v,(int,float))})

# 3 gamma values vs cited clauses
print('gamma_m0_steel', K.GAMMA_M0_STEEL, '(IS800 8.4.1/IRC22 603.3.3.2 docstring says 1.10)')
print('gamma_v_stud default 1.25 (cl 606.3.1 signature)')

# 4 scaling of moment capacity: double As -> capacity should NOT double (nonlinear), but xu doubles; check formula
fy,As,d,fck,b=250,1000,500,25,1000
m1=D._moment_capacity_kNm(fy,As,d,fck,b)
m2=D._moment_capacity_kNm(fy,2*As,d,fck,b)
xu1=0.87*fy*As/(0.36*fck*b); xu2=0.87*fy*2*As/(0.36*fck*b)
exp2=0.87*fy*2*As*(d-0.42*xu2)/1e6
show('moment_capacity 2x As (hand)', round(exp2,3), round(m2,3))

# 5 shear capacity scaling: double tw -> double Vd
s1=I.cl_603_3_3_2_plastic_shear_resistance('i_major',250,fabrication='welded',d=1000,tw=10)
s2=I.cl_603_3_3_2_plastic_shear_resistance('i_major',250,fabrication='welded',d=1000,tw=20)
show('shear Vd 2x tw -> 2x', round(s1['Vd_kN']*2,2), round(s2['Vd_kN'],2))
