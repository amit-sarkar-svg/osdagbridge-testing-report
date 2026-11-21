"""L1: validators. Register every key of the three validators x value bank."""
from tests.extreme.registry import register
from tests.extreme.bank import value_bank, enum_bank
from tests.extreme import oracles
from tests.extreme.base import base_input
import sys

sys.path.insert(0, "/Users/macbook/Projects/OsdagBridge/src")
from osdagbridge.core.bridge_types.plate_girder.validator import BridgeInputValidator

_bv = BridgeInputValidator()

def make_l1(key, family, value, tag_extra=""):
    def fn():
        d = base_input()
        d[key] = value
        return d
    def oracle(d):
        method = getattr(_bv, f"validate_{family}_inputs")
        return oracles.or_l1_no_raise(method(key, d))
    return fn, oracle

def register_l1():
    # (key, family) pairs
    pairs = [
        ("geometry.span", "basic"),
        ("geometry.carriageway_width", "basic"),
        ("geometry.skew_angle", "basic"),
        ("geometry.footpath", "basic"),
        ("geometry.include_median", "basic"),
        ("typical_section.girder_spacing", "additional"),
        ("typical_section.no_of_girders", "additional"),
        ("typical_section.deck_thickness", "additional"),
        ("typical_section.footpath_width", "additional"),
        ("typical_section.footpath_thickness", "additional"),
        ("typical_section.crash_barrier.width", "additional"),
        ("typical_section.crash_barrier.height", "additional"),
        ("typical_section.crash_barrier.load", "additional"),
        ("typical_section.crash_barrier.post_spacing", "additional"),
        ("typical_section.median.width", "additional"),
        ("typical_section.median.height", "additional"),
        ("typical_section.median.load", "additional"),
        ("typical_section.median.post_spacing", "additional"),
        ("typical_section.railing.height", "additional"),
        ("typical_section.railing.width", "additional"),
        ("typical_section.railing.load_value", "additional"),
        ("typical_section.wearing_course.thickness", "additional"),
        ("typical_section.wearing_course.density", "additional"),
        ("material.girder.e", "material"),
        ("material.girder.fy", "material"),
        ("material.girder.fu", "material"),
        ("material.girder.poisson", "material"),
        ("material.girder.g", "material"),
        ("material.girder.density", "material"),
        ("material.girder.thermal", "material"),
        ("material.deck.fck", "material"),
        ("material.deck.fctm", "material"),
        ("material.deck.ecm", "material"),
        ("material.deck.density", "material"),
        ("material.deck.thermal", "material"),
        ("material.cross_bracing.fy", "material"),
        ("material.cross_bracing.e", "material"),
        ("material.cross_bracing.g", "material"),
        ("material.cross_bracing.density", "material"),
        ("material.end_diaphragm.fy", "material"),
        ("material.end_diaphragm.e", "material"),
        ("material.end_diaphragm.density", "material"),
        ("location.latitude", "map"),
        ("location.longitude", "map"),
        ("typical_section.weather.wind_speed", "weather"),
        ("typical_section.weather.zone", "weather"),
        ("typical_section.weather.max_temp", "weather"),
        ("typical_section.weather.min_temp", "weather"),
    ]
    vals = value_bank()
    for key, family in pairs:
        for vname, v in vals.items():
            fn, oracle = make_l1(key, family, v, f"{vname}")
            register(id=f"L1.{family}.{key.split('.')[-1]}.{vname}", layer="L1",
                     oracle="never_raise", fn=fn, expect="or_l1_no_raise",
                     timeout=30, tags=("l1", family, vname))
    # enum variants on a dropdown
    for key, family in [("geometry.footpath", "basic"), ("geometry.include_median", "basic"),
                        ("design_mode", "basic")]:
        for ev in enum_bank():
            fn, oracle = make_l1(key, family, ev, "enum")
            register(id=f"L1.{family}.{key.split('.')[-1]}.enum.{ev[:12]}", layer="L1",
                     oracle="never_raise", fn=fn, expect="or_l1_no_raise",
                     timeout=30, tags=("l1", family, "enum"))
