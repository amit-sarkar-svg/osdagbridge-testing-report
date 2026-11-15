#!/usr/bin/env python
"""One-off probe (NOT a test case, NOT a baseline): verifies that the full
design() pipeline runs headless in this conda env and measures runtime so the
per-case timeout can be sized. Output goes to evidence/pipeline_probe/.
"""
import sys, time, traceback
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "evidence" / "pipeline_probe"
OUT.mkdir(parents=True, exist_ok=True)

from osdagbridge.core.utils.common import KEY_SPAN, KEY_CARRIAGEWAY_WIDTH, KEY_SKEW_ANGLE
from osdagbridge.core.bridge_types.plate_girder.defaults import (
    BASIC_INPUT_DICT, solve_extend_basic_input_dict,
)
from osdagbridge.core.bridge_types.plate_girder.plategirderbridge import PlateGirderBridge

d = dict(BASIC_INPUT_DICT)
d[KEY_SPAN] = 20.0
d[KEY_CARRIAGEWAY_WIDTH] = 4.25
d[KEY_SKEW_ANGLE] = 0.0

sys.path.insert(0, str(REPO / "scripts"))
from ui_emulation import prime_material_inputs
prime_material_inputs(d, mode="osi_load")

solve_extend_basic_input_dict(d)
(OUT / "probe_input.yaml").write_text(__import__("yaml").dump(d))

b = PlateGirderBridge()
t0 = time.time()
try:
    b.set_input(d)
    b.design()
    status = "design_ok"
except Exception:
    status = "design_error"
    (OUT / "probe_traceback.txt").write_text(traceback.format_exc())
runtime = time.time() - t0
print(f"PROBE RESULT: {status} in {runtime:.1f}s")
sys.exit(0 if status == "design_ok" else 1)
