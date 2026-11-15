"""Validator-limit tests for the Plate Girder Bridge module.

These exercise BridgeInputValidator directly (the same class the UI and the
 OSI loader use). Each test asserts the documented boundary behaviour:
values just inside the limit pass (None), values just outside are corrected.
"""
import os
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]

from osdagbridge.core.utils.common import (
    KEY_SPAN, KEY_CARRIAGEWAY_WIDTH, KEY_SKEW_ANGLE,
    KEY_INCLUDE_MEDIAN,
    KEY_MATERIAL_GIRDER_DENSITY, KEY_MATERIAL_GIRDER_FY, KEY_MATERIAL_GIRDER_FU,
    KEY_MATERIAL_GIRDER_E, KEY_MATERIAL_GIRDER_G, KEY_MATERIAL_GIRDER_POISSON,
    KEY_MATERIAL_GIRDER_THERMAL,
    KEY_MATERIAL_DECK_DENSITY, KEY_MATERIAL_DECK_FCK, KEY_MATERIAL_DECK_FCTM,
    KEY_MATERIAL_DECK_ECM, KEY_MATERIAL_DECK_THERMAL,
)
from osdagbridge.core.bridge_types.plate_girder.validator import BridgeInputValidator


@pytest.fixture(scope="module")
def validator():
    return BridgeInputValidator()


# (key, inside-low, outside-low, inside-high, outside-high, corrected-low, corrected-high)
STEEL_CASES = [
    ("density", KEY_MATERIAL_GIRDER_DENSITY, 50.0, 49.9, 120.0, 120.1, 50.0, 120.0),
    ("fy",      KEY_MATERIAL_GIRDER_FY,      100.0, 99.9, 1200.0, 1200.1, 100.0, 1200.0),
    ("fu",      KEY_MATERIAL_GIRDER_FU,      100.0, 99.9, 1500.0, 1500.1, 100.0, 1500.0),
    ("E",       KEY_MATERIAL_GIRDER_E,       100.0, 99.9, 300.0, 300.1, 100.0, 300.0),
    ("G",       KEY_MATERIAL_GIRDER_G,       30.0, 29.9, 120.0, 120.1, 30.0, 120.0),
    ("poisson", KEY_MATERIAL_GIRDER_POISSON, 0.0, -0.01, 0.5, 0.51, 0.0, 0.5),
    ("thermal", KEY_MATERIAL_GIRDER_THERMAL, 1.0, 0.9, 30.0, 30.1, 1.0, 30.0),
]

DECK_CASES = [
    ("density", KEY_MATERIAL_DECK_DENSITY, 18.0, 17.9, 28.0, 28.1, 18.0, 28.0),
    ("fck",     KEY_MATERIAL_DECK_FCK,     10.0, 9.9, 80.0, 80.1, 10.0, 80.0),
    ("fctm",    KEY_MATERIAL_DECK_FCTM,    0.5, 0.49, 6.0, 6.1, 0.5, 6.0),
    ("Ecm",     KEY_MATERIAL_DECK_ECM,     15.0, 14.9, 50.0, 50.1, 15.0, 50.0),
    ("thermal", KEY_MATERIAL_DECK_THERMAL, 5.0, 4.9, 15.0, 15.1, 5.0, 15.0),
]


@pytest.mark.parametrize(
    "name,key,in_lo,out_lo,in_hi,out_hi,corr_lo,corr_hi", STEEL_CASES,
    ids=[c[0] for c in STEEL_CASES],
)
def test_custom_steel_bounds(validator, name, key, in_lo, out_lo, in_hi, out_hi, corr_lo, corr_hi):
    assert validator.validate_material_inputs(key, {key: in_lo}) is None
    assert validator.validate_material_inputs(key, {key: in_hi}) is None
    corr, msg = validator.validate_material_inputs(key, {key: out_lo})
    assert corr == corr_lo, msg
    corr, msg = validator.validate_material_inputs(key, {key: out_hi})
    assert corr == corr_hi, msg


@pytest.mark.parametrize(
    "name,key,in_lo,out_lo,in_hi,out_hi,corr_lo,corr_hi", DECK_CASES,
    ids=[c[0] for c in DECK_CASES],
)
def test_custom_deck_bounds(validator, name, key, in_lo, out_lo, in_hi, out_hi, corr_lo, corr_hi):
    assert validator.validate_material_inputs(key, {key: in_lo}) is None
    assert validator.validate_material_inputs(key, {key: in_hi}) is None
    corr, msg = validator.validate_material_inputs(key, {key: out_lo})
    assert corr == corr_lo, msg
    corr, msg = validator.validate_material_inputs(key, {key: out_hi})
    assert corr == corr_hi, msg


def test_span_bounds(validator):
    assert validator.validate_basic_inputs(KEY_SPAN, {KEY_SPAN: 20.0}) is None
    assert validator.validate_basic_inputs(KEY_SPAN, {KEY_SPAN: 45.0}) is None
    corr, _ = validator.validate_basic_inputs(KEY_SPAN, {KEY_SPAN: 19.9})
    assert corr == 20.0
    corr, _ = validator.validate_basic_inputs(KEY_SPAN, {KEY_SPAN: 45.1})
    assert corr == 45.0
    corr, _ = validator.validate_basic_inputs(KEY_SPAN, {KEY_SPAN: "abcd"})
    assert corr == 20.0


def test_carriageway_bounds(validator):
    assert validator.validate_basic_inputs(KEY_CARRIAGEWAY_WIDTH, {KEY_CARRIAGEWAY_WIDTH: 4.25}) is None
    assert validator.validate_basic_inputs(KEY_CARRIAGEWAY_WIDTH, {KEY_CARRIAGEWAY_WIDTH: 23.6}) is None
    corr, _ = validator.validate_basic_inputs(KEY_CARRIAGEWAY_WIDTH, {KEY_CARRIAGEWAY_WIDTH: 4.2})
    assert corr is not None
    corr, _ = validator.validate_basic_inputs(KEY_CARRIAGEWAY_WIDTH, {KEY_CARRIAGEWAY_WIDTH: 23.7})
    assert corr == 23.6


def test_carriageway_with_median_min(validator):
    inputs = {KEY_CARRIAGEWAY_WIDTH: 5.0, KEY_INCLUDE_MEDIAN: "Yes"}
    corr, msg = validator.validate_basic_inputs(KEY_CARRIAGEWAY_WIDTH, inputs)
    assert corr == 7.5, msg


def test_skew_bounds(validator):
    assert validator.validate_basic_inputs(KEY_SKEW_ANGLE, {KEY_SKEW_ANGLE: -15.0}) is None
    assert validator.validate_basic_inputs(KEY_SKEW_ANGLE, {KEY_SKEW_ANGLE: 15.0}) is None
    corr, _ = validator.validate_basic_inputs(KEY_SKEW_ANGLE, {KEY_SKEW_ANGLE: -15.1})
    assert corr == -15.0
    corr, _ = validator.validate_basic_inputs(KEY_SKEW_ANGLE, {KEY_SKEW_ANGLE: 15.1})
    assert corr == 15.0


def test_nan_span_behaviour(validator):
    """Documentary test: records how NaN span is treated by the validator."""
    result = validator.validate_basic_inputs(KEY_SPAN, {KEY_SPAN: float("nan")})
    # Record actual: either None (NaN accepted!) or a correction tuple.
    if result is None:
        pytest.fail("NaN span accepted by validate_basic_inputs (no error returned)")
    else:
        corr, msg = result
        assert msg  # whatever it returns must carry a message
