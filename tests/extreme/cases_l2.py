"""L2: layout solver — fine grid over span/cw/skew + footpath/median/mode."""
from tests.extreme.registry import register
from tests.extreme.base import base_input
from tests.extreme import oracles
import sys

sys.path.insert(0, "/Users/macbook/Projects/OsdagBridge/src")

def make_l2(tag, overrides):
    def fn():
        d = base_input()
        d.update(overrides)
        return d
    def oracle(d):
        from osdagbridge.core.bridge_types.plate_girder.defaults import solve_extend_basic_input_dict
        solve_extend_basic_input_dict(d)
        return oracles.or_l2_solve_valid(d)
    return fn, oracle

def register_l2():
    spans = [20, 20.5, 21, 25, 30, 35, 40, 44.9, 45, 45.1]
    cws   = [4.25, 4.5, 7.5, 10.5, 12, 18.1, 23.6, 23.61, 23.9, 25]
    skews = [-15, -7.5, -0.0, 0.0, 7.5, 15]
    foots = [None, "One Footway", "Both Footpaths"]
    meds  = ["No", "Yes"]
    modes = ["Optimized", "Custom"]
    i = 0
    for s in spans:
        fn, o = make_l2("span", {"geometry.span": s})
        register(id=f"L2.grid.span.{s}", layer="L2", oracle="solve_valid", fn=fn, expect="or_l2_solve_valid",
                 timeout=60, tags=("l2", "grid", "span"))
    for cw in cws:
        fn, o = make_l2("cw", {"geometry.carriageway_width": cw})
        register(id=f"L2.grid.cw.{cw}", layer="L2", oracle="solve_valid", fn=fn, expect="or_l2_solve_valid",
                 timeout=60, tags=("l2", "grid", "cw"))
    for sk in skews:
        fn, o = make_l2("skew", {"geometry.skew_angle": sk})
        register(id=f"L2.grid.skew.{sk}", layer="L2", oracle="solve_valid", fn=fn, expect="or_l2_solve_valid",
                 timeout=60, tags=("l2", "grid", "skew"))
    for fp in foots:
        fn, o = make_l2("foot", {"geometry.footpath": fp})
        register(id=f"L2.grid.footpath.{str(fp)}", layer="L2", oracle="solve_valid", fn=fn, expect="or_l2_solve_valid",
                 timeout=60, tags=("l2", "grid", "footpath"))
    for md in meds:
        fn, o = make_l2("med", {"geometry.include_median": md})
        register(id=f"L2.grid.median.{md}", layer="L2", oracle="solve_valid", fn=fn, expect="or_l2_solve_valid",
                 timeout=60, tags=("l2", "grid", "median"))
    for m in modes:
        fn, o = make_l2("mode", {"geometry.design_mode": m})
        register(id=f"L2.grid.mode.{m}", layer="L2", oracle="solve_valid", fn=fn, expect="or_l2_solve_valid",
                 timeout=60, tags=("l2", "grid", "mode"))
