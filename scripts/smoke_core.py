"""Smoke test: verify core modules import and validators work headlessly (no GUI)."""
import sys, traceback

try:
    from osdagbridge.core.utils.common import (
        KEY_SPAN, KEY_CARRIAGEWAY_WIDTH, KEY_SKEW_ANGLE, SPAN_MIN, SPAN_MAX,
        KEY_MATERIAL_GIRDER_FY, KEY_MATERIAL_GIRDER_DENSITY, KEY_MATERIAL_DECK_FCK,
    )
    from osdagbridge.core.bridge_types.plate_girder.validator import BridgeInputValidator
    from osdagbridge.core.bridge_types.plate_girder.defaults import BASIC_INPUT_DICT, solve_extend_basic_input_dict
    from osdagbridge.core.utils.osi_validator import validate_osi_inputs
    from osdagbridge.core.bridge_types.plate_girder.plategirderbridge import PlateGirderBridge
    print("imports OK")
    print("SPAN limits:", SPAN_MIN, SPAN_MAX)

    v = BridgeInputValidator()
    # span just outside
    print("span 45.1 ->", v.validate_basic_inputs(KEY_SPAN, {KEY_SPAN: 45.1}))
    print("span 44.9 ->", v.validate_basic_inputs(KEY_SPAN, {KEY_SPAN: 44.9}))
    print("fy 1200.1 ->", v.validate_material_inputs(KEY_MATERIAL_GIRDER_FY, {KEY_MATERIAL_GIRDER_FY: 1200.1}))
    print("fck 80.1 ->", v.validate_material_inputs(KEY_MATERIAL_DECK_FCK, {KEY_MATERIAL_DECK_FCK: 80.1}))
    r = validate_osi_inputs({"geometry.span": "abcd"})
    print("osi bad span valid?", r.is_valid, r.errors)
    b = PlateGirderBridge()
    print("PlateGirderBridge() OK")
except Exception:
    traceback.print_exc()
    sys.exit(1)
