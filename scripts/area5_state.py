#!/usr/bin/env python3
"""Area 5 (multi-run/session state) + Area 3 (CAD parameter propagation) checks.

Runs a real headless design sequence on ONE PlateGirderBridge object
(A -> B -> C -> A) plus an "all limit states off" variant, and one fresh-object
A run. For every run it saves input_before / input_after / output_dict and a
result entry. Afterwards it compares run 4 with run 1 (state leakage), and the
fresh run with run 1 (object reuse), and checks the 3D-CAD DTO against the
inputs (skew sign, girder count, spacing, footpath/railing width).

No baseline .osi is required: inputs are built from BASIC_INPUT_DICT with the
UI's own priming + solve steps (same pipeline as scripts/case_runner.py).

Usage:
    python scripts/area5_state.py            # full sequence (~6-8 min)
    python scripts/area5_state.py --dry-run  # print the planned runs only
    python scripts/area5_state.py --help
"""
import argparse
import hashlib
import json
import sys
import time
import traceback
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "evidence" / "area5"
sys.path.insert(0, str(REPO / "scripts"))


def json_safe(obj):
    import types
    if isinstance(obj, types.MappingProxyType):
        return json_safe(dict(obj))
    if isinstance(obj, dict):
        return {str(k): json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [json_safe(v) for v in obj]
    if isinstance(obj, (bool, int, str)) or obj is None:
        return obj
    if isinstance(obj, float):
        import math
        return obj if math.isfinite(obj) else repr(obj)
    tolist = getattr(obj, "tolist", None)
    if callable(tolist):
        return json_safe(tolist())
    item = getattr(obj, "item", None)
    if callable(item):
        try:
            return json_safe(item())
        except Exception:
            pass
    try:
        json.dumps(obj)
        return obj
    except (TypeError, ValueError):
        return repr(obj)


def fingerprint(obj) -> str:
    return hashlib.sha256(json.dumps(json_safe(obj), sort_keys=True).encode()).hexdigest()


def make_input(span, cw, skew, footpath="None", limit_states_off=False):
    from osdagbridge.core.utils.common import (
        KEY_SPAN, KEY_CARRIAGEWAY_WIDTH, KEY_SKEW_ANGLE, KEY_FOOTPATH,
        KEY_DO_ULS_BENDING, KEY_DO_ULS_SHEAR, KEY_DO_ULS_LTB, KEY_DO_ULS_TRANSVERSE,
        KEY_DO_ULS_LONG_SHEAR, KEY_DO_ULS_FATIGUE, KEY_DO_SLS_STRESS,
        KEY_DO_SLS_LONG_SHEAR, KEY_DO_SLS_DEFLECTION, KEY_DO_SLS_CRACK_WIDTH,
    )
    from osdagbridge.core.bridge_types.plate_girder.defaults import (
        BASIC_INPUT_DICT, solve_extend_basic_input_dict,
    )
    from ui_emulation import prime_material_inputs

    d = dict(BASIC_INPUT_DICT)
    d.update({KEY_SPAN: span, KEY_CARRIAGEWAY_WIDTH: cw, KEY_SKEW_ANGLE: skew, KEY_FOOTPATH: footpath})
    prime_material_inputs(d, mode="osi_load")
    solve_extend_basic_input_dict(d)
    if limit_states_off:
        for k in (KEY_DO_ULS_BENDING, KEY_DO_ULS_SHEAR, KEY_DO_ULS_LTB, KEY_DO_ULS_TRANSVERSE,
                  KEY_DO_ULS_LONG_SHEAR, KEY_DO_ULS_FATIGUE, KEY_DO_SLS_STRESS,
                  KEY_DO_SLS_LONG_SHEAR, KEY_DO_SLS_DEFLECTION, KEY_DO_SLS_CRACK_WIDTH):
            d[k] = False
    return d


def cad_probe(bridge):
    """3D-CAD parameter DTO vs the input dictionary (Area 3)."""
    from osdagbridge.core.utils.common import KEY_SPAN, KEY_CARRIAGEWAY_WIDTH, KEY_SKEW_ANGLE
    try:
        dto = bridge.get_3d_cad_parameters()
    except Exception as exc:
        return {"error": f"{type(exc).__name__}: {exc}", "traceback": traceback.format_exc()}
    inp = bridge.input_dict
    return {
        "inputs": {k: inp.get(k) for k in (KEY_SPAN, KEY_CARRIAGEWAY_WIDTH, KEY_SKEW_ANGLE,
                                          "typical_section.footpath_width",
                                          "typical_section.railing.width",
                                          "typical_section.no_of_footpaths")},
        "dto": {name: getattr(dto, name, "<missing>") for name in (
            "span_length_L", "carriageway_width", "skew_angle", "num_girders",
            "girder_spacing", "footpath_config", "footpath_width", "railing_width",
            "deck_thickness")},
    }


def run_one(bridge, label, data, outdir):
    d = dict(data)
    rec = {"label": label, "status": None}
    (outdir / f"{label}_input_before.yaml").write_text(__import__("yaml").dump(json_safe(d)))
    t0 = time.time()
    try:
        bridge.set_input(d)
        bridge.design()
        rec["status"] = "design_ok"
    except Exception as exc:
        rec["status"] = "design_error"
        rec["error"] = f"{type(exc).__name__}: {exc}"
        (outdir / f"{label}_traceback.txt").write_text(traceback.format_exc())
    rec["runtime_s"] = round(time.time() - t0, 1)
    after = json_safe(getattr(bridge, "input_dict", {}))
    out = json_safe(getattr(bridge, "output_dict", {}))
    (outdir / f"{label}_input_after.yaml").write_text(__import__("yaml").dump(after))
    (outdir / f"{label}_output.json").write_text(json.dumps(out, indent=1))
    rec["input_fingerprint"] = fingerprint(after)
    rec["output_fingerprint"] = fingerprint(out)
    return rec


def diff_outputs(a, b):
    """Top-level and one-level diff of two output dictionaries."""
    diffs = []
    for k in sorted(set(a) | set(b)):
        va, vb = a.get(k), b.get(k)
        if va == vb:
            continue
        if isinstance(va, dict) and isinstance(vb, dict):
            for kk in sorted(set(va) | set(vb)):
                if va.get(kk) != vb.get(kk):
                    diffs.append(f"{k}.{kk}")
        else:
            diffs.append(k)
    return diffs


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true", help="print the planned run sequence and exit")
    ap.add_argument("--out", default=str(OUT), help="output directory")
    args = ap.parse_args()

    plan = [
        ("A1", dict(span=20.0, cw=4.25, skew=0.0)),
        ("B", dict(span=25.0, cw=7.5, skew=0.0)),
        ("C", dict(span=30.0, cw=9.0, skew=10.0, footpath="Both Sides")),
        ("A2", dict(span=20.0, cw=4.25, skew=0.0)),
        ("LIMITSOFF", dict(span=20.0, cw=4.25, skew=0.0, limit_states_off=True)),
        ("A_fresh", dict(span=20.0, cw=4.25, skew=0.0)),
    ]
    print("planned runs:", ", ".join(f"{n}{p}" for n, p in plan))
    if args.dry_run:
        return

    from osdagbridge.core.bridge_types.plate_girder.plategirderbridge import PlateGirderBridge
    outdir = Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)

    inputs = {n: make_input(**p) for n, p in plan}
    results, outputs = {}, {}

    bridge = PlateGirderBridge()  # ONE object for A1->B->C->A2
    for name in ("A1", "B", "C", "A2"):
        results[name] = run_one(bridge, name, inputs[name], outdir)
        if name in ("A1", "C"):
            results[name]["cad"] = cad_probe(bridge)
        outputs[name] = json.loads((outdir / f"{name}_output.json").read_text())
        print(f"{name}: {results[name]['status']} in {results[name]['runtime_s']}s")

    # all-limit-states-off and fresh-object A
    for name in ("LIMITSOFF", "A_fresh"):
        b = PlateGirderBridge()
        results[name] = run_one(b, name, inputs[name], outdir)
        if name == "A_fresh":
            results[name]["cad"] = cad_probe(b)
        outputs[name] = json.loads((outdir / f"{name}_output.json").read_text())
        print(f"{name}: {results[name]['status']} in {results[name]['runtime_s']}s")

    checks = {
        "A1_vs_A2_same_object": {
            "run4_output_fingerprint": results["A2"]["output_fingerprint"],
            "run1_output_fingerprint": results["A1"]["output_fingerprint"],
            "identical_output": results["A1"]["output_fingerprint"] == results["A2"]["output_fingerprint"],
            "input_fingerprint_equal": results["A1"]["input_fingerprint"] == results["A2"]["input_fingerprint"],
            "output_diff_top_keys": diff_outputs(outputs["A1"], outputs["A2"]),
        },
        "A1_vs_A_fresh": {
            "identical_output": results["A1"]["output_fingerprint"] == results["A_fresh"]["output_fingerprint"],
            "output_diff_top_keys": diff_outputs(outputs["A1"], outputs["A_fresh"]),
        },
        "A1_vs_LIMITSOFF": {
            "identical_output": results["A1"]["output_fingerprint"] == results["LIMITSOFF"]["output_fingerprint"],
            "output_diff_top_keys": diff_outputs(outputs["A1"], outputs["LIMITSOFF"]),
        },
    }
    report = {"results": results, "checks": checks}
    (outdir / "area5_report.json").write_text(json.dumps(report, indent=1))
    print(json.dumps(checks, indent=1))
    print(f"wrote {outdir / 'area5_report.json'}")


if __name__ == "__main__":
    main()
