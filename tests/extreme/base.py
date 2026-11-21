import sys, os
sys.path.insert(0, "/Users/macbook/Projects/OsdagBridge/src")
sys.path.insert(0, "/Users/macbook/Projects/osdagbridge-testing-report")
import yaml

_base_cache = None

def base_input():
    """Try test_cases/baseline.osi first, then defaults + solve_extend."""
    global _base_cache
    if _base_cache is not None:
        return dict(_base_cache)
    d = None
    p = "/Users/macbook/Projects/osdagbridge-testing-report/test_cases/baseline.osi"
    if os.path.exists(p):
        try:
            d = yaml.safe_load(open(p))
        except Exception as e:
            print(f"[base_input] load baseline.osi failed: {e}")
    if not d or not d.get("geometry.span"):
        from osdagbridge.core.bridge_types.plate_girder.defaults import (
            BASIC_INPUT_DICT, solve_extend_basic_input_dict)
        d = dict(BASIC_INPUT_DICT)
        try:
            solve_extend_basic_input_dict(d)
        except Exception as e:
            print(f"[base_input] solve_extend_basic_input_dict raised: {e}")
    _base_cache = d
    return dict(_base_cache)
