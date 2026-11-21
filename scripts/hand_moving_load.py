"""Hand calculation: absolute maximum bending moment of a vehicle (axle loads, spacings) moving over a simply supported span.
Class A (IRC 6): axles kN [27,27,114,114,68,68,68,68], spacings m [1.1,3.2,1.2,4.3,3.0,3.0,3.0].
70R wheeled (IRC 6): axles kN [80,120,120,170,170,170,170], spacings m [3.96,1.52,2.13,1.37,3.05,1.37].
Brute force: vehicle front position stepped 1 mm over [0, L + vehicle length]; moment evaluated at every axle position."""
import sys
V={'ClassA':([27,27,114,114,68,68,68,68],[1.1,3.2,1.2,4.3,3.0,3.0,3.0]),
   '70R_wheeled':([80,120,120,170,170,170,170],[3.96,1.52,2.13,1.37,3.05,1.37])}
def mmax(L,P,s,step=0.005):
    off=[0.0]; [off.append(off[-1]+d) for d in s]; Lv=off[-1]; best=0
    x=0.0
    while x<=L+Lv:
        pos=[x-o for o in off]; loads=[(p,a) for p,a in zip(P,pos) if 0<=a<=L]
        if loads:
            Ra=sum(p*(L-a) for p,a in loads)/L
            for _,a0 in loads:
                M=Ra*a0-sum(p*(a0-a) for p,a in loads if a<a0)
                best=max(best,M)
        x+=step
    return best
if __name__=='__main__':
    for L in (20,25,30,40):
        r={k:round(mmax(L,*v),1) for k,v in V.items()}
        print(f'L={L:>3} m  ClassA one train={r["ClassA"]:8.1f} kNm  two lanes={2*r["ClassA"]:8.1f}  70R wheeled={r["70R_wheeled"]:8.1f} kNm')
