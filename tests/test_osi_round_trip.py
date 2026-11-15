"""OSI round-trip test.

dict -> yaml.dump -> yaml.safe_load -> dict must be equal, and the loaded dict
must still validate and (once the baseline exists) produce the same design.

The YAML round trip itself runs on a synthetic-but-valid flat dict built with
solve_extend_basic_input_dict; the design-equality part is skipped until
test_cases/baseline.osi exists.
"""
from pathlib import Path

import pytest
import yaml

from osdagbridge.core.utils.common import (
    KEY_SPAN, KEY_CARRIAGEWAY_WIDTH, KEY_SKEW_ANGLE,
)
from osdagbridge.core.bridge_types.plate_girder.defaults import (
    BASIC_INPUT_DICT, solve_extend_basic_input_dict,
)
from osdagbridge.core.utils.osi_validator import validate_osi_inputs

REPO = Path(__file__).resolve().parents[1]
BASELINE = REPO / "test_cases" / "baseline.osi"


def _build_default_dict() -> dict:
    d = dict(BASIC_INPUT_DICT)
    d[KEY_SPAN] = 30.0
    d[KEY_CARRIAGEWAY_WIDTH] = 7.5
    d[KEY_SKEW_ANGLE] = 0.0
    solve_extend_basic_input_dict(d)
    return d


def test_yaml_round_trip_dict_equality():
    d = _build_default_dict()
    dumped = yaml.dump(d)
    loaded = yaml.safe_load(dumped)
    assert loaded == d


def test_yaml_round_trip_validates():
    d = _build_default_dict()
    loaded = yaml.safe_load(yaml.dump(d))
    result = validate_osi_inputs(loaded)
    assert result.is_valid, result.error_text()


@pytest.mark.skipif(not BASELINE.exists(), reason="baseline.osi not yet saved from the app")
def test_baseline_round_trip_design_equality():
    """Load baseline, re-dump, load again, both dicts equal and both validate."""
    first = yaml.safe_load(BASELINE.read_text())
    reloaded = yaml.safe_load(yaml.dump(first))
    assert reloaded == first
    for data in (first, reloaded):
        result = validate_osi_inputs(data)
        assert result.is_valid, result.error_text()
