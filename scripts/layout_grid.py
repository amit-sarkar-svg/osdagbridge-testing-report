#!/usr/bin/env python3
"""W2 Layout solver grid sweep (no design run).

Calls solve_extend_basic_input_dict over a grid of valid inputs and checks
layout invariants.  Never mutates OsdagBridge source; deep-copies the base
dict for every case.
"""
from __future__ import annotations

import copy
import csv
import math
import sys
from pathlib import Path

sys.path.insert(0, "/Users/macbook/Projects/OsdagBridge/src")
from osdagbridge.core.bridge_types.plate_girder.defaults import (
    BASIC_INPUT_DICT,
    solve_extend_basic_input_dict,
)
from osdagbridge.core.utils.common import (
    KEY_CARRIAGEWAY_WIDTH,
    KEY_CB_WIDTH,
    KEY_MD_WIDTH,
    KEY_RL_WIDTH,
    KEY_SKEW_ANGLE,
    KEY_SPAN,
    KEY_TS_DECK_OVERHANG,
    KEY_TS_FOOTPATH_WIDTH,
    KEY_TS_GIRDER_SPACING,
    KEY_TS_NO_OF_FOOTPATHS,
    KEY_TS_NO_OF_GIRDERS,
    KEY_TS_OVERALL_WIDTH,
)

REPO = Path("/Users/macbook/Projects/osdagbridge-testing-report")
TEST_CASES = REPO / "test_cases"
OUT_CSV = TEST_CASES / "layout_grid_results.csv"

BASE_KEYS = {
    KEY_SPAN: 30.0,
    KEY_CARRIAGEWAY_WIDTH: 10.5,
    KEY_SKEW_ANGLE: 0.0,
    "geometry.include_median": "No",
    "geometry.footpath": "None",
    "geometry.design_mode": "Optimized",
}

SPANS = [20.0, 25.0, 30.0, 35.0, 40.0, 45.0]
SPAN_EDGE = [19.9999999, 20.0000001, 44.9999999, 45.0000001]
CWS = [4.25, 7.5, 10.5, 15.0, 23.6]
CW_EDGE = [4.2499999, 4.25, 7.4999999, 7.5, 7.5000001, 23.5999999, 23.6, 23.6000001]
SKEWS = [-15.0, -7.5, -0.0, 0.0, 7.5, 15.0]
FOOTPATHS = ["None", "Single Side", "Both Sides"]
MEDIANS = ["No", "Yes"]

PASS1_SPANS = [20.0, 30.0, 40.0, 45.0]
PASS1_CWS = [4.25, 10.5, 23.6]
PASS1_SKEWS = [-15.0, 0.0, 15.0]
PASS1_FOOTPATHS = ["None", "Single Side", "Both Sides"]
PASS1_MEDIANS = ["No", "Yes"]


def make_base() -> dict:
    d = dict(BASIC_INPUT_DICT)
    d.update(BASE_KEYS)
    return d


def make_case(base: dict, span, cw, skew, footpath, median) -> dict:
    d = copy.deepcopy(base)
    d[KEY_SPAN] = span
    d[KEY_CARRIAGEWAY_WIDTH] = cw
    d[KEY_SKEW_ANGLE] = skew
    d["geometry.footpath"] = footpath
    d["geometry.include_median"] = median
    return d


def extract(d: dict) -> dict:
    return {
        KEY_SPAN: d.get(KEY_SPAN),
        KEY_CARRIAGEWAY_WIDTH: d.get(KEY_CARRIAGEWAY_WIDTH),
        KEY_SKEW_ANGLE: d.get(KEY_SKEW_ANGLE),
        "geometry.include_median": d.get("geometry.include_median"),
        "geometry.footpath": d.get("geometry.footpath"),
        KEY_TS_NO_OF_GIRDERS: d.get(KEY_TS_NO_OF_GIRDERS),
        KEY_TS_GIRDER_SPACING: d.get(KEY_TS_GIRDER_SPACING),
        KEY_TS_DECK_OVERHANG: d.get(KEY_TS_DECK_OVERHANG),
        KEY_TS_OVERALL_WIDTH: d.get(KEY_TS_OVERALL_WIDTH),
        KEY_TS_NO_OF_FOOTPATHS: d.get(KEY_TS_NO_OF_FOOTPATHS),
        KEY_TS_FOOTPATH_WIDTH: d.get(KEY_TS_FOOTPATH_WIDTH),
        KEY_RL_WIDTH: d.get(KEY_RL_WIDTH),
        KEY_MD_WIDTH: d.get(KEY_MD_WIDTH),
        KEY_CB_WIDTH: d.get(KEY_CB_WIDTH),
        KEY_CB_LOAD: d.get("typical_section.crash_barrier.load"),
        KEY_MD_LOAD: d.get("typical_section.median.load"),
        KEY_RL_WIDTH: d.get(KEY_RL_WIDTH),
    }


def check_invariants(case_id: str, out: dict) -> list:
    violations = []

    def scan(node, path=""):
        if isinstance(node, dict):
            for k, v in node.items():
                scan(v, f"{path}.{k}" if path else k)
        elif isinstance(node, list):
            for i, v in enumerate(node):
                scan(v, f"{path}[{i}]")
        elif isinstance(node, (int, float)) and not isinstance(node, bool):
            if math.isnan(node) or math.isinf(node):
                violations.append(f"{path}={node} (non-finite)")
            elif node < 0 and path != "geometry.skew_angle":
                violations.append(f"{path}={node} (negative)")

    scan(out)

    ng = out.get(KEY_TS_NO_OF_GIRDERS)
    spacing = out.get(KEY_TS_GIRDER_SPACING)
    overhang = out.get(KEY_TS_DECK_OVERHANG)
    overall = out.get(KEY_TS_OVERALL_WIDTH)

    if not isinstance(ng, int) or ng < 2:
        violations.append(f"no_of_girders={ng!r} not int>=2")
    if spacing is not None and (not isinstance(spacing, (int, float)) or spacing <= 0):
        violations.append(f"girder_spacing={spacing!r} not >0")
    if overhang is not None and overhang < 0:
        violations.append(f"deck_overhang={overhang} negative")

    cw = out.get(KEY_CARRIAGEWAY_WIDTH)
    n_fp = out.get(KEY_TS_NO_OF_FOOTPATHS)
    fp_w = out.get(KEY_TS_FOOTPATH_WIDTH)
    rl_w = out.get(KEY_RL_WIDTH)
    md_w = out.get(KEY_MD_WIDTH)
    cb_w = out.get(KEY_CB_WIDTH)
    if all(v is not None for v in (cw, n_fp, fp_w, rl_w, md_w, cb_w, overall)):
        median_in = str(out.get("geometry.include_median", "No")).strip().lower()
        if median_in == "yes":
            expected = 2 * cw + 2 * cb_w + n_fp * fp_w + n_fp * rl_w + md_w
        else:
            expected = cw + 2 * cb_w + n_fp * fp_w + n_fp * rl_w + md_w
        if abs(overall - expected) > 1e-6:
            violations.append(
                f"overall_width={overall} != sum={expected} "
                f"(diff={overall-expected:.6g})"
            )

    return violations


def run_case(case_id: str, base: dict, span, cw, skew, footpath, median) -> dict:
    inp = make_case(base, span, cw, skew, footpath, median)
    inp_copy = copy.deepcopy(inp)

    result = {
        "case": case_id,
        "span": span,
        "cw": cw,
        "skew": skew,
        "footpath": footpath,
        "median": median,
        "status": "ok",
        "exception": "",
        "violations": "",
        "girders": None,
        "spacing": None,
        "overall_width": None,
        "mutated": None,
        "idempotent": None,
    }

    try:
        solve_extend_basic_input_dict(inp)
    except Exception as e:
        result["status"] = "exception"
        result["exception"] = f"{type(e).__name__}: {e}"
        return result

    result["violations"] = "; ".join(check_invariants(case_id, inp))
    result["girders"] = inp.get(KEY_TS_NO_OF_GIRDERS)
    result["spacing"] = inp.get(KEY_TS_GIRDER_SPACING)
    result["overall_width"] = inp.get(KEY_TS_OVERALL_WIDTH)

    result["mutated"] = inp != inp_copy

    inp2 = copy.deepcopy(inp)
    try:
        solve_extend_basic_input_dict(inp2)
        out2 = {
            KEY_TS_NO_OF_GIRDERS: inp2.get(KEY_TS_NO_OF_GIRDERS),
            KEY_TS_GIRDER_SPACING: inp2.get(KEY_TS_GIRDER_SPACING),
            KEY_TS_DECK_OVERHANG: inp2.get(KEY_TS_DECK_OVERHANG),
            KEY_TS_OVERALL_WIDTH: inp2.get(KEY_TS_OVERALL_WIDTH),
        }
        out1 = {
            KEY_TS_NO_OF_GIRDERS: inp.get(KEY_TS_NO_OF_GIRDERS),
            KEY_TS_GIRDER_SPACING: inp.get(KEY_TS_GIRDER_SPACING),
            KEY_TS_DECK_OVERHANG: inp.get(KEY_TS_DECK_OVERHANG),
            KEY_TS_OVERALL_WIDTH: inp.get(KEY_TS_OVERALL_WIDTH),
        }
        result["idempotent"] = out1 == out2
    except Exception as e:
        result["idempotent"] = f"EXC {type(e).__name__}"

    return result


def pass1_cases(base: dict):
    cases = []
    for s in PASS1_SPANS:
        for c in PASS1_CWS:
            cases.append((s, c, 0.0, "None", "No"))
    for c in PASS1_CWS:
        for f in PASS1_FOOTPATHS:
            cases.append((30.0, c, 0.0, f, "No"))
    for c in PASS1_CWS:
        for m in PASS1_MEDIANS:
            cases.append((30.0, c, 0.0, "None", m))
    for s in PASS1_SKEWS:
        cases.append((30.0, 10.5, s, "None", "No"))
    seen = set()
    uniq = []
    for c in cases:
        key = tuple(c)
        if key not in seen:
            seen.add(key)
            uniq.append(c)
    return uniq


def main():
    TEST_CASES.mkdir(exist_ok=True)
    (REPO / "evidence/logs").mkdir(exist_ok=True)

    base = make_base()
    cases = pass1_cases(base)
    print(f"W2 pass-1 cases: {len(cases)}")

    results = []
    for i, (span, cw, skew, footpath, median) in enumerate(cases):
        cid = f"W2-{i+1:03d}"
        r = run_case(cid, base, span, cw, skew, footpath, median)
        results.append(r)
        status = r["status"]
        extra = ""
        if r["status"] == "ok":
            extra = f"girders={r['girders']} spacing={r['spacing']} mut={r['mutated']} idem={r['idempotent']}"
            if r["violations"]:
                extra += f" VIOLATIONS={r['violations']}"
        else:
            extra = f"EXC={r['exception']}"
        print(
            f"{cid} span={span} cw={cw} skew={skew} foot={footpath} med={median} -> {status} {extra}",
            flush=True,
        )

    fields = [
        "case", "span", "cw", "skew", "footpath", "median", "status", "exception",
        "violations", "girders", "spacing", "overall_width", "mutated", "idempotent",
    ]
    with OUT_CSV.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(results)
    print(f"wrote {OUT_CSV} ({len(results)} rows)")

    ok = sum(1 for r in results if r["status"] == "ok")
    exc = sum(1 for r in results if r["status"] == "exception")
    viol = sum(1 for r in results if r["status"] == "ok" and r["violations"])
    mut = sum(1 for r in results if r["mutated"])
    nonidem = sum(1 for r in results if r["idempotent"] is False)
    print(
        f"SUMMARY: total={len(results)} ok={ok} exceptions={exc} "
        f"violations={viol} mutated={mut} non_idempotent={nonidem}"
    )


if __name__ == "__main__":
    main()
