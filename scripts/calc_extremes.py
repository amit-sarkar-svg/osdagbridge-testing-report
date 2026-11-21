#!/usr/bin/env python3
"""Track K: numeric extremes on pure calc functions; check validator limits first."""
import sys, math
sys.path.insert(0,'/Users/macbook/Projects/OsdagBridge/src')
from osdagbridge.core.utils.codes.irc22_2015 import IRC22_2014 as I
from osdagbridge.core.utils.codes.is800_2007 import IS800_2007 as S
from osdagbridge.core.bridge_types.plate_girder import deckdesign as D

vals=[0.0, 1e-9, 1e9, -1.0, float('nan'), float('inf')]
def call(fn,kwargs,label):
    out=[]
    for v in vals:
        kw=dict(kwargs); kw[list(kwargs)[0]]=v  # override first arg
        try:
            r=fn(**kw)
            # extract numeric result if dict
            if isinstance(r,dict):
                nums={k:x for k,x in r.items() if isinstance(x,float)}
                bad=[k for k,x in nums.items() if math.isnan(x) or math.isinf(x) or x<0]
                s=f"dict(bad={bad})"
            elif isinstance(r,float):
                s=f"{r:.3g}"+(" NAN/INF/NEG" if (math.isnan(r) or math.isinf(r) or r<0) else "")
            else: s=str(r)[:25]
            out.append(f"{v!r}->{s}")
        except Exception as e:
            out.append(f"{v!r}->EXC {type(e).__name__}")
    print(f"{label}: "+" | ".join(out))

print("=== deckdesign._moment_capacity_kNm (vary fy) ===")
call(D._moment_capacity_kNm,{'fy_MPa':250,'As_mm2':1000,'d_mm':500,'fck_MPa':25},'moment_capacity fy')
print("=== deckdesign._required_steel_mm2 (vary M) ===")
call(D._required_steel_mm2,{'M_ULS_kNm':100,'fy_MPa':500,'d_mm':500,'fck_MPa':25},'required_steel M')
print("=== v_Rd_c (vary As) ===")
call(D._v_Rd_c_MPa,{'As_mm2':1000,'d_mm':500,'fck_MPa':25},'v_Rd_c As')
print("=== _min_steel_mm2 (vary fy) ===")
call(D._min_steel_mm2,{'fctm_MPa':2.5,'fy_MPa':500,'d_mm':200},'min_steel fy')
print("=== cl_603_3_3_2_plastic_shear (vary fyw) ===")
call(I.cl_603_3_3_2_plastic_shear_resistance,{'section_type':'i_major','fyw':250,'fabrication':'welded','d':1000,'tw':10},'plastic_shear fyw')
print("=== Kv (vary c) ===")
call(S.cl_8_4_2_2_K_v_Simple_postcritical,{'support':'intermediate','c':100,'d':1000},'Kv c')
