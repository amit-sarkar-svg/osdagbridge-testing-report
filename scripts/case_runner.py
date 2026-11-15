#!/usr/bin/env python
"""Run ONE test case end-to-end in this process (invoked as a subprocess by run_headless.py).

Usage: python case_runner.py <osi_path> <out_dir> [--no-solve]

Pipeline mirrors the app's Load .osi -> Design flow:
  yaml.safe_load -> validate_osi_inputs -> solve_extend_basic_input_dict
  -> PlateGirderBridge().set_input(d) -> design() -> reset()

Writes into <out_dir>:
  input_before.yaml   dict as loaded (pre solve)
  input_after_solve.yaml   dict after solve_extend_basic_input_dict
  input_after_design.yaml  bridge.input_dict after design() (records in-place mutation)
  output_dict.json    JSON-safe output_dict
  validator.json      OSI validation result
  result.json         status, exception class/message, traceback, timings
Exits 0 even when design raises (status is in result.json); exits 2 on usage error.
"""
from __future__ import annotations

import json
import math
import sys
import time
import traceback
from pathlib import Path

import yaml


def json_safe(obj):
    """Best-effort conversion of output structures to JSON-serialisable values."""
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
        return obj if math.isfinite(obj) else ("__nonfinite__", obj)
    # numpy scalars / arrays
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


def dump_yaml(obj, path: Path):
    try:
        path.write_text(yaml.dump(json_safe(obj)))
    except Exception as exc:
        path.write_text(f"# yaml dump failed: {exc}\n")


def main() -> int:
    osi_path, out_dir = Path(sys.argv[1]), Path(sys.argv[2])
    no_solve = "--no-solve" in sys.argv
    out_dir.mkdir(parents=True, exist_ok=True)
    result = {"case": osi_path.stem, "osi": str(osi_path)}

    t0 = time.time()
    try:
        data = yaml.safe_load(osi_path.read_text())
        result["load_yaml"] = "ok"
    except Exception as exc:
        result["load_yaml"] = f"error: {exc}"
        result["status"] = "yaml_error"
        (out_dir / "result.json").write_text(json.dumps(result, indent=2))
        return 0

    dump_yaml(data, out_dir / "input_before.yaml")

    # --- OSI load-time validation (same as template_page.loadOSI_inputs) ---
    from osdagbridge.core.utils.osi_validator import validate_osi_inputs
    val = validate_osi_inputs(data)
    (out_dir / "validator.json").write_text(json.dumps({
        "is_valid": val.is_valid,
        "errors": val.errors,
        "warnings": val.warnings,
        "corrected_values": {k: json_safe(v) for k, v in val.corrected_values.items()},
    }, indent=2))
    result["validator_valid"] = val.is_valid
    result["validator_errors"] = len(val.errors)

    if not val.is_valid:
        result["status"] = "osi_rejected"
        result["runtime_s"] = round(time.time() - t0, 2)
        (out_dir / "result.json").write_text(json.dumps(result, indent=2))
        return 0

    # --- solve_extend_basic_input_dict (UI does this at load + before design) ---
    from osdagbridge.core.bridge_types.plate_girder.defaults import (
        BASIC_INPUT_DICT, solve_extend_basic_input_dict,
    )
    if not no_solve:
        # 1) emulate the UI's _prime_material_inputs (always runs before Design)
        prime_mode = "in_session" if "--prime-mode=in_session" in sys.argv else "osi_load"
        try:
            from ui_emulation import prime_material_inputs
            prime_material_inputs(data, mode=prime_mode)
            result["prime"] = prime_mode
        except Exception as exc:
            result["prime"] = f"error: {type(exc).__name__}: {exc}"
            result["prime_traceback"] = traceback.format_exc()
            # continue: a priming failure is itself evidence
        # 2) solve layout (template_page L648 / L867)
        try:
            solve_extend_basic_input_dict(data)
            result["solve"] = "ok"
        except Exception as exc:
            result["solve"] = "error"
            result["solve_exception"] = f"{type(exc).__name__}: {exc}"
            result["solve_traceback"] = traceback.format_exc()
            result["status"] = "solve_error"
            result["runtime_s"] = round(time.time() - t0, 2)
            (out_dir / "result.json").write_text(json.dumps(result, indent=2))
            dump_yaml(data, out_dir / "input_after_solve.yaml")
            return 0
        dump_yaml(data, out_dir / "input_after_solve.yaml")

    # --- set_input + design ---
    from osdagbridge.core.bridge_types.plate_girder.plategirderbridge import PlateGirderBridge
    bridge = PlateGirderBridge()
    try:
        bridge.set_input(data)
        result["set_input"] = "ok"
    except Exception as exc:
        result["set_input"] = f"error: {exc}"
        result["status"] = "set_input_error"
        result["set_input_traceback"] = traceback.format_exc()
        result["runtime_s"] = round(time.time() - t0, 2)
        (out_dir / "result.json").write_text(json.dumps(result, indent=2))
        return 0

    t_design = time.time()
    try:
        bridge.design()
        result["design"] = "ok"
        result["status"] = "design_ok"
    except Exception as exc:
        result["design"] = "error"
        result["design_exception_type"] = type(exc).__name__
        result["design_exception_msg"] = str(exc)
        result["design_traceback"] = traceback.format_exc()
        result["status"] = "design_error"
    finally:
        result["design_runtime_s"] = round(time.time() - t_design, 2)

    # capture post-design state BEFORE reset()
    try:
        dump_yaml(bridge.input_dict, out_dir / "input_after_design.yaml")
    except Exception as exc:
        (out_dir / "input_after_design.yaml").write_text(f"# dump failed: {exc}\n")
    try:
        (out_dir / "output_dict.json").write_text(
            json.dumps(json_safe(bridge.output_dict), indent=2))
    except Exception as exc:
        (out_dir / "output_dict.json").write_text(json.dumps({"dump_error": str(exc)}))

    try:
        bridge.reset()
        result["reset"] = "ok"
    except Exception as exc:
        result["reset"] = f"error: {exc}"

    result["runtime_s"] = round(time.time() - t0, 2)
    (out_dir / "result.json").write_text(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
