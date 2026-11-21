"""Hand check of the static-vehicle placement: axles from the program's own IRC6 tables placed with the vehicle's
local origin at global x=0 (as analyser.py:1641/1834 does), versus the vehicle moved to its worst position.
Max moment over all sections of a simply supported span (single vehicle line)."""
import sys
sys.path.insert(0,'/Users/macbook/Projects/OsdagBridge/src')
def mom(L,loads):
    loads=[(p,a) for p,a in loads if 0<=a<=L]
    if not loads: return 0.0
    Ra=sum(p*(L-a) for p,a in loads)/L; best=0
    for k in range(0,int(L*200)+1):
        x=k/200; best=max(best,Ra*x-sum(p*(x-a) for p,a in loads if a<x))
    return best
def worst(L,P,X):
    Lv=max(X)-min(X); best=0; s=-max(X)
    while s<=L-min(X):
        best=max(best,mom(L,[(p,s+x) for p,x in zip(P,X)])); s+=0.05
    return best
def main():
    from osdagbridge.core.utils.codes.irc6_2017 import IRC6_2017
    veh={'ClassA':IRC6_2017.cl_204_1_ClassA_vehicle(),'Class70R':IRC6_2017.cl_204_1_Class70R_vehicle_wheel()}
    for name,d in veh.items():
        P=[w/1000.0 for w in d['wheel_loads']]; X=[float(x) for x in d['x'][:len(P)]]
        print(name,'axle loads kN',[round(p,1) for p in P],'x (local, m)',[round(x,2) for x in X])
        for L in (20.0,25.0,30.0,40.0):
            f=mom(L,[(p,x) for p,x in zip(P,X)]); w=worst(L,P,X)
            print(f'  L={L:4.0f}  fixed at x=0: {f:8.1f} kNm   worst position: {w:8.1f} kNm   ratio={f/w:5.2f}')
if __name__=='__main__': main()
