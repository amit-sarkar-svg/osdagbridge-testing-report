#!/usr/bin/env python3
"""W4 STEP 4: Full-key mutation sweep on the OSI loader (fast version).

For every key in the base dict (flattened to dotted paths) and each value
class, build a mutated dict, then run osi_validator.validate() directly
(skipping the slow yaml.dump/safe_load round-trip).

Output:
  test_cases/os_sweep_results.csv   one row per (key, value-class)
"""
from __future__ import annotations

import copy
import csv
import sys
from pathlib import Path

sys.path.insert(0, "/Users/macbook/Projects/OsdagBridge/src")
import yaml
from osdagbridge.core.bridge_types.plate_girder.defaults import BASIC_INPUT_DICT
from osdagbridge.core.utils.osi_validator import OsiInputValidator

REPO = Path("/Users/macbook/Projects/osdagbridge-testing-report")
TEST_CASES = REPO / "test_cases"
BASELINE = TEST_CASES / "baseline.osi"
OUT_CSV = TEST_CASES / "os_sweep_results.csv"


def build_base():
    d = yaml.safe_load(BASELINE.read_text())
    return d


def flatten(d, prefix=""):
    out = {}
    for k, v in d.items():
        j = f"{prefix}.{k}" if prefix else str(k)
        if isinstance(v, dict):
            out.update(flatten(v, j))
        else:
            out[j] = v
    return out


VALUE_CLASSES = [
    ("none", None),
    ("empty_str", ""),
    ("spaces", "  "),
    ("bool_true", True),
    ("bool_false", False),
    ("nan", float("nan")),
    ("inf", float("inf")),
    ("ninf", float("-inf")),
    ("huge", 1e308),
    ("tiny", 1e-300),
    ("neg", -5.0),
    ("zero", 0.0),
    ("text_unit", "30 m"),
    ("text_comma", "30,5"),
    ("enum_lower", "highway bridge"),
    ("enum_upper", "HIGHWAY BRIDGE"),
    ("enum_near_miss", "Single side"),
]


def run_one(osv, base, key, vname, val):
    res = {
        "key": key,
        "vclass": vname,
        "value": repr(val),
        "status": "ok",
        "exception": "",
        "validator": "",
        "errors": "",
        "warnings": "",
        "loaded_eq_mutated": None,
        "loaded_val": None,
    }
    try:
        mutated = copy.deepcopy(base)
        if vname == "deleted":
            mutated.pop(key, None)
            res["value"] = "<deleted>"
        elif vname == "extra_unknown_key":
            mutated["zzz.unknown.key"] = val
            res["value"] = f"extra:{val!r}"
            key = "zzz.unknown.key"
        else:
            mutated[key] = val
        result = osv.validate(mutated)
        res["validator"] = "valid" if result.is_valid else "INVALID"
        res["errors"] = "; ".join(result.errors)
        res["warnings"] = "; ".join(result.warnings)
        loaded_val = mutated.get(key)
        res["loaded_val"] = repr(loaded_val)
        if key in mutated:
            if mutated[key] == val:
                res["loaded_eq_mutated"] = "same"
            else:
                res["loaded_eq_mutated"] = f"CHANGED: {loaded_val!r}"
        else:
            res["loaded_eq_mutated"] = "DROPPED"
    except Exception as e:
        res["status"] = "exception"
        res["exception"] = f"{type(e).__name__}: {e}"
    return res


def main():
    base = build_base()
    flat = flatten(base)
    osv = OsiInputValidator()
    print(f"base keys (flat): {len(flat)}")

    results = []
    keys_sorted = sorted(flat.keys())
    print(f"sweeping {len(keys_sorted)} keys x {len(VALUE_CLASSES)} value classes "
          f"= {len(keys_sorted)*len(VALUE_CLASSES)} cases")

    count = 0
    for key in keys_sorted:
        for vname, val in VALUE_CLASSES:
            if vname == "deleted":
                res = run_one(osv, base, key, vname, None)
            elif vname == "extra_unknown_key":
                res = run_one(osv, base, "__EXTRA__", vname, val)
                res["key"] = "__EXTRA__.unknown.key"
            else:
                res = run_one(osv, base, key, vname, val)
            results.append(res)
            count += 1
            if count % 1000 == 0:
                print(f"  ... {count} cases done", flush=True)

    fields = ["key", "vclass", "value", "status", "exception",
              "validator", "errors", "warnings", "loaded_eq_mutated", "loaded_val"]
    with OUT_CSV.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(results)
    print(f"wrote {OUT_CSV} ({len(results)} rows)")

    from collections import Counter
    status_counts = Counter(r["status"] for r in results)
    print("STATUS COUNTS:", dict(status_counts))


if __name__ == "__main__":
    main()
