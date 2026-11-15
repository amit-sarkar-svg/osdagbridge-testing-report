#!/usr/bin/env python
"""Multi-run state check: A -> B -> C -> A on ONE bridge object, then the same
four runs on fresh objects. Run 4 must equal Run 1 (and fresh-object runs must
equal the same-object runs).

Inputs are the case files from the manifest (default SN01, DM01, CM01).
Writes evidence/state_check/result.json with comparison outcomes.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "evidence" / "state_check"
OUT.mkdir(parents=True, exist_ok=True)

from osdagbridge.core.utils.osi_validator import validate_osi_inputs
from osdagbridge.core.bridge_types.plate_girder.defaults import solve_extend_basic_input_dict
from osdagbridge.core.bridge_types.plate_girder.plategirderbridge import PlateGirderBridge
from ui_emulation import prime_material_inputs  # type: ignore
from case_runner import json_safe  # type: ignore (both live in scripts/)


def load_case(case_id: str) -> dict:
    path = REPO / "test_cases" / "generated" / f"{case_id}.osi"
    d = yaml.safe_load(path.read_text())
    validate_osi_inputs(d)  # raise on rejection — only valid cases go here
    if not validate_osi_inputs(d).is_valid:
        raise ValueError(f"{case_id} rejected by OSI validator; pick another case")
    # in_session priming so custom-material case values survive (value-flow check)
    prime_material_inputs(d, mode="in_session")
    solve_extend_basic_input_dict(d)
    return d


def run_on(bridge: PlateGirderBridge, d: dict) -> dict:
    bridge.set_input(d)
    bridge.design()
    out = json_safe(bridge.output_dict)
    return out


def main() -> int:
    ids = sys.argv[1:] or ["SN01", "DM01", "CM01"]
    sequence = ids + [ids[0]]  # A B C A
    data = [load_case(cid) for cid in sequence]
    fresh_inputs = [load_case(cid) for cid in sequence]  # re-solved copies for fresh runs

    one = PlateGirderBridge()
    seq_out = []
    for i, d in enumerate(data, 1):
        t0 = __import__("time").time()
        try:
            seq_out.append(run_on(one, d))
        except Exception as exc:
            OUT.joinpath("traceback.txt").write_text(__import__("traceback").format_exc())
            result = {"status": "error", "run": i, "exception": str(exc),
                      "traceback": OUT.joinpath("traceback.txt").read_text()}
            (OUT / "result.json").write_text(json.dumps(result, indent=2))
            print("STATE CHECK ERROR:", result)
            return 1
        one.reset()

    fresh_out = []
    for i, d in enumerate(fresh_inputs, 1):
        b = PlateGirderBridge()
        try:
            fresh_out.append(run_on(b, d))
        except Exception as exc:
            OUT.joinpath("traceback_fresh.txt").write_text(__import__("traceback").format_exc())
            result = {"status": "error_fresh", "run": i, "exception": str(exc)}
            (OUT / "result.json").write_text(json.dumps(result, indent=2))
            return 1
        b.reset()

    def diff(a, b, prefix=""):
        diffs = []
        keys = set(a) | set(b)
        for k in sorted(keys):
            va, vb = a.get(k), b.get(k)
            if va != vb:
                diffs.append(f"{prefix}{k}: {va!r} != {vb!r}")
        return diffs

    d41 = diff(seq_out[3], seq_out[0])               # run4 vs run1 (same object)
    d_fresh = [diff(f, s) for f, s in zip(fresh_out, seq_out)]  # fresh vs same-object per run

    result = {
        "status": "ok",
        "sequence": sequence,
        "run4_vs_run1_diff_count": len(d41),
        "run4_vs_run1_diffs_sample": d41[:40],
        "fresh_vs_sameobject_diff_counts": [len(d) for d in d_fresh],
        "fresh_vs_sameobject_diffs_sample": [d[:10] for d in d_fresh],
        "verdict_run4_equals_run1": len(d41) == 0,
        "verdict_fresh_equals_sameobject": all(len(d) == 0 for d in d_fresh),
    }
    (OUT / "result.json").write_text(json.dumps(result, indent=2))
    (OUT / "run4_vs_run1_diffs.json").write_text(json.dumps(d41, indent=2))
    print(json.dumps({k: result[k] for k in ("status", "run4_vs_run1_diff_count",
                                             "verdict_run4_equals_run1",
                                             "verdict_fresh_equals_sameobject")}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
