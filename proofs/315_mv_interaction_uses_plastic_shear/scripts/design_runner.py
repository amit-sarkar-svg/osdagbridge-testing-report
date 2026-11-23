#!/usr/bin/env python3
"""Headless design harness (build dict from defaults, run design in-process).

Subcommands:
  build <params.json> <out.json>   build a full input dict from BASIC_INPUT_DICT + params
  run <input.json> <outdir>        set_input(d); design(); save output_dict JSON + result.json
"""
from __future__ import annotations
import sys, os, json, time, traceback
from pathlib import Path
sys.path.insert(0, '/Users/macbook/Projects/OsdagBridge/src')
sys.path.insert(0, '/Users/macbook/Projects/osdagbridge-testing-report/scripts')


def build(params: dict) -> dict:
    from osdagbridge.core.bridge_types.plate_girder.defaults import BASIC_INPUT_DICT, solve_extend_basic_input_dict
    from ui_emulation import prime_material_inputs
    d = dict(BASIC_INPUT_DICT)
    for k, v in params.items():
        d[k] = v
    solve_extend_basic_input_dict(d)
    prime_material_inputs(d, mode="in_session")
    return d


def jsonable(o):
    import numpy as np
    from collections.abc import Mapping
    if o is None or isinstance(o, (bool, int, str)):
        return o
    if isinstance(o, Mapping):
        return {str(k): jsonable(v) for k, v in o.items()}
    if isinstance(o, float):
        if o != o or o in (float('inf'), float('-inf')):
            return str(o)
        return o
    if isinstance(o, (np.floating,)):
        return jsonable(float(o))
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.bool_,)):
        return bool(o)
    if isinstance(o, np.ndarray):
        return [jsonable(x) for x in o.tolist()]
    if isinstance(o, dict):
        return {str(k): jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple, set)):
        return [jsonable(x) for x in o]
    return str(o)


def run(input_path: str, outdir: str):
    out = Path(outdir); out.mkdir(parents=True, exist_ok=True)
    d = json.load(open(input_path))
    res = {'status': 'ok', 'exception_type': '', 'traceback': '', 'runtime_s': 0.0}
    t0 = time.time()
    try:
        from osdagbridge.core.bridge_types.plate_girder.plategirderbridge import PlateGirderBridge
        b = PlateGirderBridge()
        b.set_input(d)
        b.design()
        od = dict(getattr(b, 'output_dict', {}) or {})
        (out / 'output.json').write_text(json.dumps(jsonable(od)))
        res['output_top_keys'] = len(od)
    except Exception as e:
        res['status'] = 'exception'
        res['exception_type'] = f"{type(e).__name__}: {e}"
        res['traceback'] = traceback.format_exc()
    res['runtime_s'] = round(time.time() - t0, 1)
    (out / 'result.json').write_text(json.dumps(res))
    print(res['status'], res.get('exception_type',''), res['runtime_s'])


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'build':
        params = json.load(open(sys.argv[2]))
        d = build(params)
        Path(sys.argv[3]).write_text(json.dumps(jsonable(d)))
        print('built', len(d), 'keys')
    elif cmd == 'run':
        run(sys.argv[2], sys.argv[3])
