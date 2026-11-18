#!/usr/bin/env python3
"""#132 root cause: compare oblique grillage node geometry for +skew vs -skew (mirror symmetry)."""
import sys
sys.path.insert(0,'/Users/macbook/Projects/OsdagBridge/src')
import ospgrillage as og

def build(skew):
    g=og.create_grillage(bridge_name=f"sk{skew}",long_dim=30.0,width=8.4,skew=skew,
        num_long_grid=4,num_trans_grid=5,edge_beam_dist=1.05,mesh_type="Oblique")
    return g

def nodes(g):
    out={}
    for tag,spec in g.Mesh_obj.node_spec.items():
        c=spec.get('coordinate') or spec.get('coords') or spec
        out[tag]=tuple(c) if not isinstance(c,dict) else tuple(c.values())
    return out

if __name__=='__main__':
    for s in [15.0,-15.0]:
        g=build(s)
        ns=nodes(g)
        print(f"skew={s}: nnodes={len(ns)}")
        # sample first few node coords
        for tag in list(ns)[:4]:
            print('  ',tag,ns[tag])
