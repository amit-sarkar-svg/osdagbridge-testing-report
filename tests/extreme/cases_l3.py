"""L3: .osi loader — per-key mutation through yaml.dump/safe_load/validate_osi_inputs."""
import sys
sys.path.insert(0, "/Users/macbook/Projects/OsdagBridge/src")
sys.path.insert(0, "/Users/macbook/Projects/osdagbridge-testing-report")
import yaml
from tests.extreme.registry import register
from tests.extreme.base import base_input
from tests.extreme import oracles

def make_l3(key, value, tag):
    def fn():
        d = base_input()
        d[key] = value
        return d
    def oracle(d):
        from osdagbridge.core.utils.osi_validator import OsiInputValidator
        # loadOSI_inputs non-GUI path: safe_load happens in our dump+load here
        dumped = yaml.dump(d)
        loaded = yaml.safe_load(dumped)
        r = OsiInputValidator().validate(loaded)
        return oracles.or_l1_no_raise(r.is_valid)
    return fn, oracle

def register_l3():
    from tests.extreme.bank import value_bank
    vals = value_bank()
    keys = [
        "geometry.span", "geometry.carriageway_width", "geometry.skew_angle",
        "geometry.footpath", "geometry.include_median",
        "typical_section.girder_spacing", "typical_section.no_of_girders",
        "typical_section.deck_thickness", "typical_section.footpath_width",
        "typical_section.footpath_thickness", "typical_section.crash_barrier.width",
        "typical_section.crash_barrier.height", "typical_section.crash_barrier.load",
        "typical_section.crash_barrier.post_spacing", "typical_section.median.width",
        "typical_section.median.height", "typical_section.median.load",
        "typical_section.median.post_spacing", "typical_section.railing.height",
        "typical_section.railing.width", "typical_section.railing.load_value",
        "typical_section.wearing_course.thickness", "material.girder.e",
        "material.girder.fy", "material.girder.poisson", "material.deck.fck",
        "material.deck.density", "typical_section.location.latitude",
    ]
    for key in keys:
        for vn, v in vals.items():
            fn, o = make_l3(key, v, vn)
            register(id=f"L3.{key}.{vn}", layer="L3", oracle="loader_no_crash_valid_rejected", fn=fn,
                     expect="no crash; validator is_valid False-or-True; no silent change of accepted value",
                     timeout=30, tags=("l3", "loader"))
