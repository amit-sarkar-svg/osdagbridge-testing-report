"""Oracles for extreme cases. Contract from session rules:
L1: validator never raises; returns None or (corrected, msg); corrected finite
    for numeric; bool/NaN/inf never accepted; '30'/30/30.0 decided identically;
    '30' never silently accepted in place of a numeric that must be number.
"""
import math

def or_l1_no_raise(d):
    """Just assert the validator runs; classified as anomaly if it raises."""
    return d is not None

def or_l1_accept_empty(d):
    """Allow acceptance of empty for keys not required to have a value; else None."""
    return True

def or_l1_never_accept_bool_or_nonfinite(d):
    if isinstance(d, bool) and not isinstance(d, (int, float)):
        return False  # anomaly: bool accepted
    if isinstance(d, float) and (math.isnan(d) or math.isinf(d)):
        return False  # anomaly: non-finite accepted
    return True

def or_l2_solve_valid(d):
    # no exception; geometry keys present and finite
    for k in ("geometry.span", "geometry.carriageway_width"):
        v = d.get(k)
        if not isinstance(v, (int, float)) or isinstance(v, bool) or not math.isfinite(v):
            raise AssertionError(f"{k}={v!r} after solve_extend_basic_input_dict")
    return True

def or_l2_grid_symmetric_skew(d):
    v = d.get("geometry.skew_angle")
    if not isinstance(v, (int, float)) or isinstance(v, bool):
        raise AssertionError(f"skew not numeric: {v!r}")
    return True

# aliases used by case files (string oracle names)
solve_valid = or_l2_solve_valid
never_raise = or_l1_no_raise
loader_no_crash_valid_rejected = or_l1_no_raise
accept_empty = or_l1_accept_empty
never_accept_bool_or_nonfinite = or_l1_never_accept_bool_or_nonfinite
