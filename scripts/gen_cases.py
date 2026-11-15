#!/usr/bin/env python
"""Generate one mutated .osi per test case from the real app-saved baseline.

Reads  test_cases/baseline.osi  (saved from the Osdag GUI - never fabricated).
Writes test_cases/generated/<ID>.osi and test_cases/manifest.json.

A case = full copy of the baseline dict + one mutation (occasionally two that
must be consistent, e.g. median=Yes + carriageway=5.0). No invented keys:
every key we touch is verified to exist in the baseline first (except the
custom-material property keys, whose canonical names were verified against
material_properties.py get_export_fields() / common.py L67-97).
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
BASELINE = REPO / "test_cases" / "baseline.osi"
GEN_DIR = REPO / "test_cases" / "generated"
MANIFEST = REPO / "test_cases" / "manifest.json"

# keys that MUST exist in a real baseline for a case to be generated
REQUIRED_KEYS = [
    "structure.type",
    "project.location",
    "geometry.span",
    "geometry.carriageway_width",
    "geometry.include_median",
    "geometry.footpath",
    "geometry.skew_angle",
    "geometry.design_mode",
    "material.girder",
    "material.cross_bracing",
    "material.end_diaphragm",
    "material.deck",
]

NAN = float("nan")


def cases() -> list[dict]:
    """(id, area, description, mutations, expect) — expect: run|reject|unknown"""
    C: list[dict] = []
    add = C.append

    # ---------- Geometry boundaries ----------
    add(dict(id="GE01", area="geometry", desc="span 20.0 m (lower boundary, inside)",
             mut={"geometry.span": 20.0}, expect="run"))
    add(dict(id="GE02", area="geometry", desc="span 19.9 m (just outside lower limit)",
             mut={"geometry.span": 19.9}, expect="reject"))
    add(dict(id="GE03", area="geometry", desc="span 45.0 m (upper boundary, inside)",
             mut={"geometry.span": 45.0}, expect="run"))
    add(dict(id="GE04", area="geometry", desc="span 45.1 m (just outside upper limit)",
             mut={"geometry.span": 45.1}, expect="reject"))
    add(dict(id="GE05", area="geometry", desc="carriageway 4.25 m (lower boundary, inside)",
             mut={"geometry.carriageway_width": 4.25}, expect="run"))
    add(dict(id="GE06", area="geometry", desc="carriageway 4.2 m (just outside lower limit)",
             mut={"geometry.carriageway_width": 4.2}, expect="reject"))
    add(dict(id="GE07", area="geometry", desc="carriageway 23.6 m (upper boundary, inside)",
             mut={"geometry.carriageway_width": 23.6}, expect="run"))
    add(dict(id="GE08", area="geometry", desc="carriageway 23.7 m (just outside upper limit)",
             mut={"geometry.carriageway_width": 23.7}, expect="reject"))
    add(dict(id="GE09", area="geometry", desc="skew -15 deg (lower boundary, inside)",
             mut={"geometry.skew_angle": -15.0}, expect="run"))
    add(dict(id="GE10", area="geometry", desc="skew -15.1 deg (just outside)",
             mut={"geometry.skew_angle": -15.1}, expect="reject"))
    add(dict(id="GE11", area="geometry", desc="skew +15 deg (upper boundary, inside)",
             mut={"geometry.skew_angle": 15.0}, expect="run"))
    add(dict(id="GE12", area="geometry", desc="skew +15.1 deg (just outside)",
             mut={"geometry.skew_angle": 15.1}, expect="reject"))

    # ---------- Footpath / median combinations ----------
    add(dict(id="CO01", area="layout-combo", desc="footpath None (explicit)",
             mut={"geometry.footpath": "None"}, expect="run"))
    add(dict(id="CO02", area="layout-combo", desc="footpath Single Side",
             mut={"geometry.footpath": "Single Side"}, expect="run"))
    add(dict(id="CO03", area="layout-combo", desc="footpath Both Sides",
             mut={"geometry.footpath": "Both Sides"}, expect="run"))
    add(dict(id="CO04", area="layout-combo", desc="include_median Yes (default carriageway)",
             mut={"geometry.include_median": "Yes"}, expect="run"))
    add(dict(id="CO05", area="layout-combo", desc="median Yes + carriageway 5.0 (<7.5 with median, IRC5 cl104.3.1)",
             mut={"geometry.include_median": "Yes", "geometry.carriageway_width": 5.0}, expect="reject"))
    add(dict(id="CO06", area="layout-combo", desc="median Yes + carriageway 7.5 (boundary, inside)",
             mut={"geometry.include_median": "Yes", "geometry.carriageway_width": 7.5}, expect="run"))

    # ---------- Design mode ----------
    add(dict(id="DM01", area="design-mode", desc="design_mode Custom",
             mut={"geometry.design_mode": "Custom"}, expect="run"))
    add(dict(id="DM02", area="design-mode", desc="design_mode Optimized (explicit)",
             mut={"geometry.design_mode": "Optimized"}, expect="run"))

    # ---------- Custom materials (in-range) ----------
    add(dict(id="CM01", area="custom-material", desc="custom girder steel, all values in-range",
             mut={"material.girder": "QA_CustomSteel",
                  "material.girder.density": "77.0", "material.girder.fy": "355.0",
                  "material.girder.fu": "490.0", "material.girder.e": "210.0",
                  "material.girder.g": "81.0", "material.girder.poisson": "0.30",
                  "material.girder.thermal": "11.7"}, expect="run"))
    add(dict(id="CM02", area="custom-material", desc="custom girder steel, density 49.9 (out-of-range low)",
             mut={"material.girder": "QA_CustomSteelLoD",
                  "material.girder.density": "49.9", "material.girder.fy": "355.0",
                  "material.girder.fu": "490.0", "material.girder.e": "210.0",
                  "material.girder.g": "81.0", "material.girder.poisson": "0.30",
                  "material.girder.thermal": "11.7"}, expect="reject"))
    add(dict(id="CM03", area="custom-material", desc="custom girder steel, fy 1200.1 (out-of-range high)",
             mut={"material.girder": "QA_CustomSteelHiFy",
                  "material.girder.density": "77.0", "material.girder.fy": "1200.1",
                  "material.girder.fu": "490.0", "material.girder.e": "210.0",
                  "material.girder.g": "81.0", "material.girder.poisson": "0.30",
                  "material.girder.thermal": "11.7"}, expect="reject"))
    add(dict(id="CM04", area="custom-material", desc="custom girder steel, E 99.9 (out-of-range low)",
             mut={"material.girder": "QA_CustomSteelLoE",
                  "material.girder.density": "77.0", "material.girder.fy": "355.0",
                  "material.girder.fu": "490.0", "material.girder.e": "99.9",
                  "material.girder.g": "81.0", "material.girder.poisson": "0.30",
                  "material.girder.thermal": "11.7"}, expect="reject"))
    add(dict(id="CM05", area="custom-material", desc="custom girder steel, Fu 1500.1 (out-of-range high)",
             mut={"material.girder": "QA_CustomSteelHiFu",
                  "material.girder.density": "77.0", "material.girder.fy": "355.0",
                  "material.girder.fu": "1500.1", "material.girder.e": "210.0",
                  "material.girder.g": "81.0", "material.girder.poisson": "0.30",
                  "material.girder.thermal": "11.7"}, expect="reject"))
    add(dict(id="CM06", area="custom-material", desc="custom girder steel, Poisson 0.51 (out-of-range high)",
             mut={"material.girder": "QA_CustomSteelPoi",
                  "material.girder.density": "77.0", "material.girder.fy": "355.0",
                  "material.girder.fu": "490.0", "material.girder.e": "210.0",
                  "material.girder.g": "81.0", "material.girder.poisson": "0.51",
                  "material.girder.thermal": "11.7"}, expect="reject"))
    add(dict(id="CM07", area="custom-material", desc="custom girder steel, thermal 0.9 (out-of-range low)",
             mut={"material.girder": "QA_CustomSteelThm",
                  "material.girder.density": "77.0", "material.girder.fy": "355.0",
                  "material.girder.fu": "490.0", "material.girder.e": "210.0",
                  "material.girder.g": "81.0", "material.girder.poisson": "0.30",
                  "material.girder.thermal": "0.9"}, expect="reject"))
    add(dict(id="CM08", area="custom-material", desc="custom deck concrete, all values in-range",
             mut={"material.deck": "QA_CustomConcrete",
                  "material.deck.density": "25.0", "material.deck.fck": "35.0",
                  "material.deck.fctm": "3.5", "material.deck.ecm": "32.0",
                  "material.deck.thermal": "10.0"}, expect="run"))
    add(dict(id="CM09", area="custom-material", desc="custom deck concrete, fck 9.9 (out-of-range low)",
             mut={"material.deck": "QA_CustomConcreteLoFck",
                  "material.deck.density": "25.0", "material.deck.fck": "9.9",
                  "material.deck.fctm": "3.5", "material.deck.ecm": "32.0",
                  "material.deck.thermal": "10.0"}, expect="reject"))
    add(dict(id="CM10", area="custom-material", desc="custom deck concrete, Ecm 50.1 (out-of-range high)",
             mut={"material.deck": "QA_CustomConcreteHiEcm",
                  "material.deck.density": "25.0", "material.deck.fck": "35.0",
                  "material.deck.fctm": "3.5", "material.deck.ecm": "50.1",
                  "material.deck.thermal": "10.0"}, expect="reject"))
    add(dict(id="CM11", area="custom-material", desc="custom cross-bracing steel (grade name + material.cross_bracing.*)",
             mut={"material.cross_bracing": "QA_CustomCBSteel",
                  "material.cross_bracing.density": "77.0", "material.cross_bracing.fy": "355.0",
                  "material.cross_bracing.fu": "490.0", "material.cross_bracing.e": "210.0",
                  "material.cross_bracing.g": "81.0", "material.cross_bracing.poisson": "0.30",
                  "material.cross_bracing.thermal": "11.7"}, expect="run"))
    add(dict(id="CM12", area="custom-material", desc="custom end-diaphragm steel (grade name + material.end_diaphragm.*)",
             mut={"material.end_diaphragm": "QA_CustomEDSteel",
                  "material.end_diaphragm.density": "77.0", "material.end_diaphragm.fy": "355.0",
                  "material.end_diaphragm.fu": "490.0", "material.end_diaphragm.e": "210.0",
                  "material.end_diaphragm.g": "81.0", "material.end_diaphragm.poisson": "0.30",
                  "material.end_diaphragm.thermal": "11.7"}, expect="run"))

    # ---------- Sensitivity pairs (full runs; outputs must differ) ----------
    add(dict(id="SN01", area="sensitivity", desc="baseline as-is (reference run)",
             mut={}, expect="run"))
    add(dict(id="SN02", area="sensitivity", desc="custom girder Fy 355->500 (outputs must change)",
             mut={"material.girder": "QA_CustomSteel500",
                  "material.girder.density": "77.0", "material.girder.fy": "500.0",
                  "material.girder.fu": "490.0", "material.girder.e": "210.0",
                  "material.girder.g": "81.0", "material.girder.poisson": "0.30",
                  "material.girder.thermal": "11.7"}, expect="run"))
    add(dict(id="SN03", area="sensitivity", desc="custom girder E 210->150 (outputs must change)",
             mut={"material.girder": "QA_CustomSteelE150",
                  "material.girder.density": "77.0", "material.girder.fy": "355.0",
                  "material.girder.fu": "490.0", "material.girder.e": "150.0",
                  "material.girder.g": "81.0", "material.girder.poisson": "0.30",
                  "material.girder.thermal": "11.7"}, expect="run"))
    add(dict(id="SN04", area="sensitivity", desc="custom girder density 77->50 (self-weight must change)",
             mut={"material.girder": "QA_CustomSteelD50",
                  "material.girder.density": "50.0", "material.girder.fy": "355.0",
                  "material.girder.fu": "490.0", "material.girder.e": "210.0",
                  "material.girder.g": "81.0", "material.girder.poisson": "0.30",
                  "material.girder.thermal": "11.7"}, expect="run"))
    add(dict(id="SN05", area="sensitivity", desc="custom deck fck 35->60 (deck design must change)",
             mut={"material.deck": "QA_CustomConcrete60",
                  "material.deck.density": "25.0", "material.deck.fck": "60.0",
                  "material.deck.fctm": "3.5", "material.deck.ecm": "32.0",
                  "material.deck.thermal": "10.0"}, expect="run"))
    add(dict(id="SN06", area="sensitivity", desc="custom deck Ecm 32->45 (deck stiffness must change)",
             mut={"material.deck": "QA_CustomConcreteEcm45",
                  "material.deck.density": "25.0", "material.deck.fck": "35.0",
                  "material.deck.fctm": "3.5", "material.deck.ecm": "45.0",
                  "material.deck.thermal": "10.0"}, expect="run"))

    # ---------- Malformed values ----------
    add(dict(id="MF01", area="malformed", desc="span = 'abcd' (text)",
             mut={"geometry.span": "abcd"}, expect="reject"))
    add(dict(id="MF02", area="malformed", desc="span = '' (empty)",
             mut={"geometry.span": ""}, expect="reject"))
    add(dict(id="MF03", area="malformed", desc="span = -5 (negative)",
             mut={"geometry.span": -5}, expect="reject"))
    add(dict(id="MF04", area="malformed", desc="span = NaN",
             mut={"geometry.span": NAN}, expect="reject"))
    add(dict(id="MF05", area="malformed", desc="skew = 'text'",
             mut={"geometry.skew_angle": "text"}, expect="reject"))
    add(dict(id="MF06", area="malformed", desc="carriageway = NaN",
             mut={"geometry.carriageway_width": NAN}, expect="reject"))
    add(dict(id="MF07", area="malformed", desc="girder Fy = NaN (material key)",
             mut={"material.girder.fy": NAN}, expect="reject"))
    add(dict(id="MF08", area="malformed", desc="design_mode = 'Bogus'",
             mut={"geometry.design_mode": "Bogus"}, expect="reject"))
    add(dict(id="MF09", area="malformed", desc="span = 0",
             mut={"geometry.span": 0}, expect="reject"))
    add(dict(id="MF10", area="malformed", desc="span as numeric string '30.0' (must be coerced, expect run)",
             mut={"geometry.span": "30.0"}, expect="run"))
    add(dict(id="MF11", area="malformed", desc="skew = None (app normalises to 0)",
             mut={"geometry.skew_angle": None}, expect="run"))

    # ---------- Round trip / determinism support ----------
    add(dict(id="RT01", area="round-trip", desc="baseline round-trip reference (same dict re-dumped)",
             mut={}, expect="run"))
    return C


def main() -> int:
    if not BASELINE.exists():
        print("ERROR: test_cases/baseline.osi missing. Save a baseline from the GUI first "
              "(project location filled, defaults otherwise, Save Input).", file=sys.stderr)
        return 2

    baseline = yaml.safe_load(BASELINE.read_text())
    missing = [k for k in REQUIRED_KEYS if k not in baseline]
    if missing:
        print(f"ERROR: baseline is missing required keys: {missing}\n"
              "Not inventing them. Re-save the baseline from the app after opening the "
              "bridge module once.", file=sys.stderr)
        return 3

    GEN_DIR.mkdir(parents=True, exist_ok=True)
    manifest = []
    for case in cases():
        d = dict(baseline)  # shallow copy; mutations are scalar/str replacements only
        for k, v in case["mut"].items():
            d[k] = v
        path = GEN_DIR / f"{case['id']}.osi"
        path.write_text(yaml.dump(d))
        manifest.append({
            "id": case["id"], "area": case["area"], "desc": case["desc"],
            "mutations": {k: (None if (isinstance(v, float) and math.isnan(v)) else v)
                          for k, v in case["mut"].items()},
            "expect": case["expect"],
            "file": str(path.relative_to(REPO)),
        })
    MANIFEST.write_text(json.dumps(manifest, indent=2))
    print(f"Wrote {len(manifest)} cases to {GEN_DIR} and manifest {MANIFEST}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
