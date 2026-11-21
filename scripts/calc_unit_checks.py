#!/usr/bin/env python3
"""W3 STEP 3: Differential unit tests on core validators."""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

sys.path.insert(0, "/Users/macbook/Projects/OsdagBridge/src")
from hypothesis import given, settings
from hypothesis import strategies as st
from osdagbridge.core.bridge_types.plate_girder.validator import BridgeInputValidator
from osdagbridge.core.utils.common import (
    KEY_CARRIAGEWAY_WIDTH,
    KEY_SKEW_ANGLE,
    KEY_SPAN,
    KEY_MATERIAL_GIRDER_DENSITY,
    KEY_MATERIAL_GIRDER_FY,
    KEY_MATERIAL_GIRDER_FU,
    KEY_MATERIAL_GIRDER_E,
    KEY_MATERIAL_GIRDER_G,
    KEY_MATERIAL_GIRDER_POISSON,
    KEY_MATERIAL_GIRDER_THERMAL,
    KEY_MATERIAL_DECK_DENSITY,
    KEY_MATERIAL_DECK_FCK,
    KEY_MATERIAL_DECK_FCTM,
    KEY_MATERIAL_DECK_ECM,
    KEY_MATERIAL_DECK_THERMAL,
    KEY_TS_DECK_THICKNESS,
    KEY_TS_FOOTPATH_THICKNESS,
    KEY_CB_HEIGHT,
    KEY_CB_LOAD,
    KEY_MD_HEIGHT,
    KEY_MD_LOAD,
    KEY_RL_HEIGHT,
)
from osdagbridge.core.utils.osi_validator import OsiInputValidator

REPO = Path("/Users/macbook/Projects/osdagbridge-testing-report")
LOG = REPO / "evidence/logs" / "trackJ_unit_checks.txt"
LOG.parent.mkdir(parents=True, exist_ok=True)

bv = BridgeInputValidator()
osv = OsiInputValidator()

BASIC_KEYS = {
    KEY_SPAN: (20.0, 45.0),
    KEY_CARRIAGEWAY_WIDTH: (4.25, 23.6),
    KEY_SKEW_ANGLE: (-15.0, 15.0),
}
MATERIAL_KEYS = {
    KEY_MATERIAL_GIRDER_DENSITY: (50.0, 120.0),
    KEY_MATERIAL_GIRDER_FY: (100.0, 1200.0),
    KEY_MATERIAL_GIRDER_FU: (100.0, 1500.0),
    KEY_MATERIAL_GIRDER_E: (100.0, 300.0),
    KEY_MATERIAL_GIRDER_G: (30.0, 120.0),
    KEY_MATERIAL_GIRDER_POISSON: (0.0, 0.5),
    KEY_MATERIAL_GIRDER_THERMAL: (1.0, 30.0),
    KEY_MATERIAL_DECK_DENSITY: (18.0, 28.0),
    KEY_MATERIAL_DECK_FCK: (10.0, 80.0),
    KEY_MATERIAL_DECK_FCTM: (0.5, 6.0),
    KEY_MATERIAL_DECK_ECM: (15.0, 50.0),
    KEY_MATERIAL_DECK_THERMAL: (5.0, 15.0),
}
ADDITIONAL_KEYS = {
    KEY_TS_DECK_THICKNESS: (100.0, 500.0),
    KEY_TS_FOOTPATH_THICKNESS: (100.0, 500.0),
    KEY_CB_HEIGHT: (0.0, 10.0),
    KEY_CB_LOAD: (0.0, 100.0),
    KEY_MD_HEIGHT: (0.0, 10.0),
    KEY_MD_LOAD: (0.0, 100.0),
    KEY_RL_HEIGHT: (1.0, 3.0),
}

ALL_KEYS = {}
ALL_KEYS.update(BASIC_KEYS)
ALL_KEYS.update(MATERIAL_KEYS)
ALL_KEYS.update(ADDITIONAL_KEYS)


def call_validator(validator_name: str, key, value):
    bv_obj = BridgeInputValidator()
    method_map = {
        "validate_basic_inputs": bv_obj.validate_basic_inputs,
        "validate_material_inputs": bv_obj.validate_material_inputs,
        "validate_additional_inputs": bv_obj.validate_additional_inputs,
    }
    fn = method_map[validator_name]
    try:
        r = fn(key, {key: value})
        return ("ok", r)
    except Exception as e:
        return ("exc", f"{type(e).__name__}: {e}")


def _validator_for(key):
    if key in BASIC_KEYS:
        return "validate_basic_inputs"
    if key in MATERIAL_KEYS:
        return "validate_material_inputs"
    return "validate_additional_inputs"


BASIC_ITEMS = list(BASIC_KEYS.items())
MATERIAL_ITEMS = list(MATERIAL_KEYS.items())
ADDITIONAL_ITEMS = list(ADDITIONAL_KEYS.items())
ALL_KEY_ITEMS = list(ALL_KEYS.items())

bad_values = st.one_of(
    st.floats(allow_nan=True, allow_infinity=True),
    st.text(),
    st.booleans(),
    st.none(),
    st.lists(st.integers()),
    st.dictionaries(st.text(), st.integers()),
    st.just("30 m"),
    st.just("30,5"),
    st.just("0x1E"),
)


@given(st.tuples(st.sampled_from(BASIC_ITEMS), bad_values))
@settings(max_examples=300, deadline=None, derandomize=True)
def test_P1_basic_inputs_validator_never_raises(item):
    (key, _lim), v = item
    st_, res = call_validator("validate_basic_inputs", key, v)
    assert st_ == "ok", f"validate_basic_inputs({key!r}, {v!r}) raised {res}"


@given(st.tuples(st.sampled_from(MATERIAL_ITEMS), bad_values))
@settings(max_examples=300, deadline=None, derandomize=True)
def test_P1_material_inputs_validator_never_raises(item):
    (key, _lim), v = item
    st_, res = call_validator("validate_material_inputs", key, v)
    assert st_ == "ok", f"validate_material_inputs({key!r}, {v!r}) raised {res}"


@given(st.tuples(st.sampled_from(ADDITIONAL_ITEMS), bad_values))
@settings(max_examples=300, deadline=None, derandomize=True)
def test_P1_additional_inputs_validator_never_raises(item):
    (key, _lim), v = item
    st_, res = call_validator("validate_additional_inputs", key, v)
    assert st_ == "ok", f"validate_additional_inputs({key!r}, {v!r}) raised {res}"


@given(st.tuples(st.sampled_from(ALL_KEY_ITEMS), bad_values))
@settings(max_examples=400, deadline=None, derandomize=True)
def test_P2_corrected_value_idempotent(item):
    (key, _lim), v = item
    st_, res = call_validator(_validator_for(key), key, v)
    if st_ != "ok":
        return
    if res is None:
        return  # validator accepted as-is (valid or unhandled key)
    corrected, msg = res
    st2, res2 = call_validator(_validator_for(key), key, corrected)
    assert st2 == "ok", f"corrected value re-validation raised: {res2}"
    assert res2 is None, (
        f"corrected value {corrected!r} for {key} is itself rejected: {res2}"
    )


@given(st.tuples(st.sampled_from(ALL_KEY_ITEMS), st.floats(allow_nan=True, allow_infinity=True)))
@settings(max_examples=400, deadline=None, derandomize=True)
def test_P3_acceptance_matches_limits(item):
    (key, lim), v = item
    lo, hi = lim
    if math.isnan(v) or math.isinf(v):
        return  # NaN/inf acceptance covered by #88
    st_, res = call_validator(_validator_for(key), key, v)
    assert st_ == "ok", f"validator raised {res}"
    if lo <= v <= hi:
        assert res is None, f"in-range {key}={v} rejected with {res}"
    else:
        assert res is not None, f"out-of-range {key}={v} accepted"


@given(
    st.one_of(
        st.booleans(),
        st.just(float("inf")),
        st.just(float("-inf")),
    )
)
@settings(max_examples=300, deadline=None, derandomize=True)
def test_P4_bool_and_nonfinite_rejected(v):
    st_, res = call_validator("validate_material_inputs", KEY_MATERIAL_GIRDER_FY, v)
    assert st_ == "ok", f"validator raised {res}"
    assert res is not None, f"bool/non-finite {v!r} accepted as-is (res={res})"


@given(st.text(min_size=1, max_size=20))
@settings(max_examples=300, deadline=None, derandomize=True)
def test_P5_text_number_consistency(s):
    st_num, res_num = call_validator("validate_material_inputs", KEY_MATERIAL_GIRDER_FY, 30)
    st_txt, res_txt = call_validator("validate_material_inputs", KEY_MATERIAL_GIRDER_FY, s)
    if st_num != "ok" or st_txt != "ok":
        return
    if res_num is None and res_txt is not None:
        return
    if res_num is not None and res_txt is None:
        assert False, f"text {s!r} accepted ({res_txt}) but 30 rejected ({res_num})"


@given(st.tuples(st.sampled_from(list(ALL_KEY_ITEMS)), st.floats(allow_nan=True, allow_infinity=True)))
@settings(max_examples=300, deadline=None, derandomize=True)
def test_P6_osi_vs_core_agreement(item):
    (key, _lim), v = item
    st_core, res_core = call_validator(_validator_for(key), key, v)
    osv = OsiInputValidator()
    res_osi = osv.validate({key: v})
    core_err = res_core is not None
    osi_err = not res_osi.is_valid
    if core_err and not osi_err:
        if key.startswith("material."):
            return
        assert False, (
            f"drift: {key}={v!r} rejected by core ({res_core}) "
            f"but accepted by osi_validator"
        )


@given(st.dictionaries(st.text(), st.floats(allow_nan=True, allow_infinity=True), max_size=5))
@settings(max_examples=200, deadline=None, derandomize=True)
def test_P7_osi_round_trip(d):
    import yaml

    dumped = yaml.dump(d)
    try:
        back = yaml.safe_load(dumped)
    except Exception as e:
        assert False, f"yaml.safe_load raised {type(e).__name__}: {e}"
    for bad_tag in ("!!python", "!!set", "!!binary"):
        assert bad_tag not in dumped, f"unsafe tag {bad_tag} in dump of {d}"


@given(st.floats(allow_nan=True, allow_infinity=True), st.floats(allow_nan=True, allow_infinity=True))
@settings(max_examples=200, deadline=None, derandomize=True)
def test_P8_weather_and_location(lat, lon):
    bv = BridgeInputValidator()
    pairs = [(lat, lon), (lon, lat), (float("nan"), float("nan"))]
    for lat_v, lon_v in pairs:
        st_, res = bv.validate_map_coordinates(str(lat_v), str(lon_v))
        assert st_ is True, f"validate_map_coordinates raised {res}"
    bv = BridgeInputValidator()
    for wind, zone, mx, mn in [(50, "II", 45, 20), ("abc", "II", 45, 20), ("50", "abc", 45, 20)]:
        st_, res = bv.validate_custom_weather_data(wind, zone, str(mx), str(mn))
        # Valid numeric inputs accepted; invalid (non-numeric wind) rejected
        try:
            float(wind)
            assert st_ is True, f"validate_custom_weather_data rejected valid input {wind}: {res}"
        except ValueError:
            assert st_ is False, f"validate_custom_weather_data accepted invalid wind '{wind}': {res}"


if __name__ == "__main__":
    import pytest

    sys.exit(
        pytest.main(
            [
                __file__,
                "-q",
                "-p",
                "no:cacheprovider",
            ]
        )
    )
