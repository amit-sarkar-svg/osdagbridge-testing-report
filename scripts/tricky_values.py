"""Build the shared 'tricky values' bank used by all QA phases (W1..W7).

Also builds test_cases/baseline.osi from defaults.BASIC_INPUT_DICT +
defaults.solve_extend_basic_input_dict when no baseline exists.

Run:  python scripts/tricky_values.py
Writes: test_cases/tricky_bank.json  (compact JSON)
        test_cases/baseline.osi     (YAML, built headless)
Prints: a compact size summary (max ~30 lines).
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

sys.path.insert(0, "/Users/macbook/Projects/OsdagBridge/src")
from osdagbridge.core.bridge_types.plate_girder.defaults import (
    BASIC_INPUT_DICT,
    solve_extend_basic_input_dict,
)

REPO = Path("/Users/macbook/Projects/osdagbridge-testing-report")
TEST_CASES = REPO / "test_cases"
TRICKY_BANK = TEST_CASES / "tricky_bank.json"
BASELINE = TEST_CASES / "baseline.osi"


# ---------------------------------------------------------------------------
# 1. Build baseline.osi headless (only if missing)
# ---------------------------------------------------------------------------
def build_baseline() -> None:
    if BASELINE.exists():
        print(f"[baseline] already exists: {BASELINE} (skipping build)")
        return
    d = dict(BASIC_INPUT_DICT)
    d["geometry.span"] = 30.0
    d["geometry.carriageway_width"] = 7.5
    d["geometry.skew_angle"] = 0.0
    d["geometry.include_median"] = "No"
    d["geometry.footpath"] = "None"
    d["geometry.design_mode"] = "Optimized"
    solve_extend_basic_input_dict(d)
    import yaml

    BASELINE.write_text(yaml.safe_dump(d, sort_keys=False))
    print(f"[baseline] built {BASELINE} (keys={len(d)})")


# ---------------------------------------------------------------------------
# 2. Tricky value bank
# ---------------------------------------------------------------------------
def _near_limits(lo: float, hi: float) -> list:
    """Return a list of values probing lo and hi limits."""
    vals = []
    for L in (lo, hi):
        vals.extend(
            [
                L,                            # exactly on limit
                L - 1e-9,                     # just inside
                L + 1e-9,                     # just outside
                L - 1e-12,                    # further inside
                math.nextafter(L, -math.inf), # float next after toward -inf
                math.nextafter(L, math.inf),  # float next after toward +inf
                L * (1 - 1e-15),              # relative -1e-15
                L + 0.01,                     # just outside (absolute)
                L - 0.01,                     # just inside (absolute)
                L + 1.0,                      # well outside (absolute)
                L - 1.0,                      # well inside (absolute)
            ]
        )
    return vals


def _enum_variants(values: list[str]) -> list:
    """Produce casing/spacing/near-miss variants for each enum value."""
    out: list = []
    for v in values:
        out.extend([v, v.lower(), v.upper(), " " + v + " ", v + " ", " " + v])
    # near-miss typos
    for v in values:
        if len(v) > 3:
            out.append(v[:-1])          # drop last char
            out.append(v + "x")         # add char
    out.extend(["", "   ", "NotAValue", "Other"])
    return out


def build_bank() -> dict:
    bank: dict = {}

    # ---- NUMERIC near limits (limits verified from common.py / validator.py) ----
    numeric = {}
    for name, lo, hi in [
        ("geometry.span", 20.0, 45.0),
        ("geometry.carriageway_width", 4.25, 23.6),
        ("geometry.carriageway_width_median", 7.5, 23.6),
        ("geometry.skew_angle", -15.0, 15.0),
        # material limits (validator.py)
        ("material.girder.density", 50.0, 120.0),
        ("material.girder.fy", 100.0, 1200.0),
        ("material.girder.fu", 100.0, 1500.0),
        ("material.girder.e", 100.0, 300.0),
        ("material.girder.g", 30.0, 120.0),
        ("material.girder.poisson", 0.0, 0.5),
        ("material.girder.thermal", 1.0, 30.0),
        ("material.deck.density", 18.0, 28.0),
        ("material.deck.fck", 10.0, 80.0),
        ("material.deck.fctm", 0.5, 6.0),
        ("material.deck.ecm", 15.0, 50.0),
        ("material.deck.thermal", 5.0, 15.0),
    ]:
        numeric[name] = _near_limits(lo, hi)
    bank["numeric_near_limits"] = numeric

    # ---- FLOAT quirks ----
    bank["float_quirks"] = [
        0.1 + 0.2,        # 0.30000000000000004
        -0.0,
        1e-300,
        5e-324,
        1.7976931348623157e308,  # max float
        2**53,                          # 9007199254740992
        2**53 + 1,                        # 9007199254740993 (not representable)
        1e15,
        123456789.123456789,
    ]

    # ---- TEXT forms of numbers ----
    bank["text_forms"] = [
        "30", "30.0", "030", " 30 ", "30 ", "+30", "3e1", "3E1",
        "30.", ".5", "30,5", "30 m", "30m", "0x1E", "1_000",
        "\u0661\u0662\u0663",   # Arabic-Indic 123
        "\uff13\uff10",        # full-width 30
        "30\u200b",             # zero-width space
        "NaN", "nan", "inf", "-inf", "Infinity",
        "None", "null", "true",
    ]

    # ---- SPECIAL ----
    bank["special"] = [
        None, "", " ", True, False, [], {}, [30], {"a": 1},
        "A" * 10000,
        "\x00", "\n30", "30\n",
    ]

    # ---- ENUM variants ----
    enum_values = {
        "geometry.footpath": ["None", "Single Side", "Both Sides"],
        "geometry.include_median": ["No", "Yes"],
        "geometry.design_mode": ["Optimized", "Custom"],
        "geometry.structure_type": ["Highway Bridge", "Other"],
        "material.girder": ["E 350A", "E 250A", "Custom"],
        "material.deck": ["M40", "M30", "Custom"],
    }
    bank["enum_variants"] = {k: _enum_variants(v) for k, v in enum_values.items()}

    # ---- COMBOS (interacting boundary pairs) ----
    combos = []
    for cw in [7.4999999, 7.5, 7.5000001]:
        combos.append(
            {
                "geometry.include_median": "Yes",
                "geometry.carriageway_width": cw,
                "geometry.span": 30.0,
                "geometry.skew_angle": 0.0,
                "geometry.footpath": "None",
                "geometry.design_mode": "Optimized",
            }
        )
    for skew in [-15.0000001, 15.0000001]:
        combos.append(
            {
                "geometry.include_median": "No",
                "geometry.carriageway_width": 10.5,
                "geometry.skew_angle": skew,
                "geometry.footpath": "None",
                "geometry.design_mode": "Optimized",
            }
        )
    for span in [19.9999999, 45.0000001]:
        for footpath in ["None", "Single Side", "Both Sides"]:
            combos.append(
                {
                    "geometry.include_median": "No",
                    "geometry.carriageway_width": 10.5,
                    "geometry.skew_angle": 0.0,
                    "geometry.footpath": footpath,
                    "geometry.span": span,
                    "geometry.design_mode": "Optimized",
                }
            )
    bank["combos"] = combos

    return bank


if __name__ == "__main__":
    build_baseline()
    bank = build_bank()
    TRICKY_BANK.write_text(json.dumps(bank, indent=2))
    total = 0
    print("=== tricky value bank ===")
    for cat, val in bank.items():
        if isinstance(val, dict):
            n = sum(len(v) if isinstance(v, list) else 1 for v in val.values())
        else:
            n = len(val)
        total += n
        print(f"  {cat:22s} {n:4d} values")
    print(f"{'TOTAL':22s} {total:4d} values")
    print(f"bank -> {TRICKY_BANK}")
    print(f"baseline -> {BASELINE}")
