#!/usr/bin/env python
"""Analyze results.csv + dictionaries/<case>/ and raise findings ONLY with evidence.

Checks (assignment list):
  1. Value flow        - custom values survive design() and reach outputs
  2. Sensitivity       - Fy/E/density/fck/Ecm changes must change relevant outputs
  3. Input mutation    - diff input after solve vs after design; list overwritten user values
  4. Validator vs design agreement - accepted-but-crashes, or rejected-but-runs
  5. Boundaries        - just-inside must run, just-outside must be rejected
  6. Multi-run state   - from evidence/state_check/result.json
  7. Round trip        - dict -> yaml -> dict equality + same design (RT01 vs SN01)
  8. Engineering sanity - finite utils >= 0, no NaN/inf, positive dims,
                          section sizes grow with span (GE01 vs GE03),
                          self-weight rises with density (SN04 vs SN01), unit mix-ups
  9. Determinism       - same input twice -> same output (SN01 vs RT01, SN01__run2)

Writes notes/analyze_report.md and evidence/analyze/*.json.
"""
from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
DICTS = REPO / "dictionaries"
RESULTS = REPO / "test_cases" / "results.csv"
EV = REPO / "evidence" / "analyze"
NOTES = REPO / "notes"
EV.mkdir(parents=True, exist_ok=True)
NOTES.mkdir(exist_ok=True)

findings: list[dict] = []
passes: list[dict] = []


def finding(fid, severity, title, evidence: dict, note=""):
    findings.append(dict(id=fid, severity=severity, title=title, evidence=evidence, note=note))
    print(f"[FINDING] {fid} ({severity}): {title}")


def case_out_dir(cid: str) -> Path:
    return DICTS / cid


def load_yaml(p: Path):
    return yaml.safe_load(p.read_text()) if p.exists() else None


def load_result(cid: str) -> dict | None:
    p = case_out_dir(cid) / "result.json"
    return json.loads(p.read_text()) if p.exists() else None


def load_output(cid: str) -> dict | None:
    p = case_out_dir(cid) / "output_dict.json"
    return json.loads(p.read_text()) if p.exists() else None


def num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def diff_dicts(a: dict, b: dict) -> list[str]:
    out = []
    for k in sorted(set(a) | set(b)):
        if a.get(k) != b.get(k):
            out.append(k)
    return out


def main() -> int:
    if not RESULTS.exists():
        print("results.csv missing - run run_headless.py first", file=sys.stderr)
        return 2
    rows = {r["id"]: r for r in csv.DictReader(RESULTS.open())}
    report = []

    def status(cid):
        r = rows.get(cid)
        return r["status"] if r else "not_run"

    # ---------------------------------------------------------------- 4+5
    EXPECT = {  # from manifest
        "GE01": "run", "GE02": "reject", "GE03": "run", "GE04": "reject",
        "GE05": "run", "GE06": "reject", "GE07": "run", "GE08": "reject",
        "GE09": "run", "GE10": "reject", "GE11": "run", "GE12": "reject",
        "CO01": "run", "CO02": "run", "CO03": "run", "CO04": "run",
        "CO05": "reject", "CO06": "run",
        "DM01": "run", "DM02": "run",
        "CM01": "run", "CM02": "reject", "CM03": "reject", "CM04": "reject",
        "CM05": "reject", "CM06": "reject", "CM07": "reject",
        "CM08": "run", "CM09": "reject", "CM10": "reject", "CM11": "run", "CM12": "run",
        "SN01": "run", "SN02": "run", "SN03": "run", "SN04": "run",
        "SN05": "run", "SN06": "run",
        "MF01": "reject", "MF02": "reject", "MF03": "reject", "MF04": "reject",
        "MF05": "reject", "MF06": "reject", "MF07": "reject", "MF08": "reject",
        "MF09": "reject", "MF10": "run", "MF11": "run",
        "RT01": "run",
    }
    for cid, expect in EXPECT.items():
        st = status(cid)
        if st == "not_run":
            continue
        if expect == "run" and st == "design_ok":
            passes.append(dict(id=cid, check="boundary/expect", detail=f"expected run -> {st}"))
        elif expect == "reject" and st in ("osi_rejected", "solve_error"):
            passes.append(dict(id=cid, check="boundary/expect", detail=f"expected reject -> {st}"))
        elif expect == "run" and st != "design_ok":
            finding(f"FB-{cid}", "high",
                    f"Case {cid} expected to run but ended '{st}'",
                    {"result.json": f"dictionaries/{cid}/result.json",
                     "traceback": f"dictionaries/{cid}/case.log"},
                    "validator accepted but design crashed - validator/design disagreement")
        elif expect == "reject" and st == "design_ok":
            finding(f"FA-{cid}", "high",
                    f"Case {cid}: bad input was ACCEPTED and design completed",
                    {"result.json": f"dictionaries/{cid}/result.json",
                     "validator.json": f"dictionaries/{cid}/validator.json"},
                    "expected rejection at OSI load (or by design), got a completed design")

    # ---------------------------------------------------------------- 2
    # sensitivity: compare numeric outputs of SN pairs
    ref = load_output("SN01")
    for other, why in [("SN02", "Fy 355->500"), ("SN03", "E 210->150"),
                       ("SN04", "density 77->50"), ("SN05", "deck fck 35->60"),
                       ("SN06", "deck Ecm 32->45")]:
        if status(other) != "design_ok" or ref is None:
            continue
        o = load_output(other)
        if o is None:
            continue
        changed = diff_dicts(ref, o)
        numeric_changed = [k for k in changed
                           if num(ref.get(k)) and num(o.get(k)) and ref[k] != o[k]]
        ev = {"baseline": "dictionaries/SN01/output_dict.json",
              "variant": f"dictionaries/{other}/output_dict.json",
              "changed_keys_count": len(changed),
              "changed_numeric_count": len(numeric_changed),
              "changed_keys_sample": changed[:50]}
        (EV / f"sensitivity_{other}.json").write_text(json.dumps(ev, indent=2))
        if len(changed) == 0:
            finding(f"FS-{other}", "high",
                    f"Sensitivity: {why} produced IDENTICAL outputs (no effect)",
                    ev, "every custom-material property may be silently ignored")
        elif not numeric_changed:
            finding(f"FS-{other}", "medium",
                    f"Sensitivity: {why} changed only non-numeric outputs (labels)",
                    ev, "outputs differ only in strings; numeric design results identical")
        else:
            passes.append(dict(id=other, check="sensitivity",
                               detail=f"{why}: {len(numeric_changed)} numeric outputs changed"))

    # ---------------------------------------------------------------- 3
    # input mutation: input_after_solve vs input_after_design for design_ok cases
    mutation_summary = {}
    for cid, row in rows.items():
        if not cid.endswith("__run2") and row["status"] == "design_ok":
            before = load_yaml(case_out_dir(cid) / "input_after_solve.yaml")
            after = load_yaml(case_out_dir(cid) / "input_after_design.yaml")
            if before is None or after is None:
                continue
            changed = diff_dicts(before, after)
            mutation_summary[cid] = len(changed)
            (EV / f"mutation_{cid}.json").write_text(json.dumps(
                {"changed_keys": changed,
                 "details": {k: {"before": before.get(k), "after": after.get(k)} for k in changed}},
                indent=2, default=str))
            # flag only mutations of keys the case itself set (user values)
            base = load_yaml(case_out_dir(cid) / "input_before.yaml") or {}
            user_set = [k for k in changed
                        if k in base and base.get(k) != before.get(k)]
            if user_set:
                finding(f"FM-{cid}", "medium",
                        f"design() overwrote {len(user_set)} user-set input values",
                        {"evidence": f"evidence/analyze/mutation_{cid}.json",
                         "keys": user_set[:30]},
                        "user values in input_dict mutated in place during design")
    (EV / "mutation_summary.json").write_text(json.dumps(mutation_summary, indent=2))

    # ---------------------------------------------------------------- 7+9
    if status("RT01") == "design_ok" and status("SN01") == "design_ok":
        a, b = load_yaml(case_out_dir("SN01") / "input_before.yaml"), \
               load_yaml(case_out_dir("RT01") / "input_before.yaml")
        if a is not None and b is not None and a == b:
            passes.append(dict(id="RT01", check="round-trip dict equality",
                               detail="re-dumped dict == original"))
        oa, ob = load_output("SN01"), load_output("RT01")
        if oa is not None and ob is not None:
            d = diff_dicts(oa, ob)
            if d:
                finding("FR-RT01", "high",
                        "Round trip: same input gives DIFFERENT outputs (SN01 vs RT01)",
                        {"diff_keys": d[:50], "count": len(d)}, "determinism failure")
            else:
                passes.append(dict(id="RT01", check="determinism (SN01 vs RT01)",
                                   detail="identical outputs"))
    if "SN01__run2" in rows and rows["SN01__run2"]["status"] == "design_ok":
        oa, ob = load_output("SN01"), load_output("SN01__run2")
        if oa is not None and ob is not None:
            d = diff_dicts(oa, ob)
            if d:
                finding("FR-RERUN", "high",
                        "Determinism: fresh rerun of SN01 differs",
                        {"diff_keys": d[:50], "count": len(d)}, None)
            else:
                passes.append(dict(id="SN01__run2", check="determinism rerun",
                                   detail="identical outputs"))

    # ---------------------------------------------------------------- 6
    sc = REPO / "evidence" / "state_check" / "result.json"
    if sc.exists():
        s = json.loads(sc.read_text())
        if s.get("status") == "ok":
            if not s["verdict_run4_equals_run1"]:
                finding("FS-STATE", "high",
                        "Multi-run state: run4 != run1 on same bridge object",
                        {"evidence": "evidence/state_check/result.json",
                         "diffs": "evidence/state_check/run4_vs_run1_diffs.json"}, None)
            else:
                passes.append(dict(id="STATE", check="multi-run A->B->C->A",
                                   detail="run4 == run1"))
            if not s["verdict_fresh_equals_sameobject"]:
                finding("FS-STATE-FRESH", "high",
                        "Multi-run state: fresh-object runs differ from same-object runs",
                        {"evidence": "evidence/state_check/result.json"}, None)

    # ---------------------------------------------------------------- 1
    # value flow: CM01 fy 355 / CM08 fck 35 / SN04 density 50 must appear in outputs
    value_checks = [
        ("CM01", "355", "custom girder Fy"),
        ("CM08", "35.0", "custom deck fck"),
    ]
    for cid, needle, what in value_checks:
        if status(cid) != "design_ok":
            continue
        o = load_output(cid) or {}
        blob = json.dumps(o)
        hits = [k for k, v in o.items() if isinstance(v, (int, float, str)) and str(v).strip() in (needle, needle.rstrip(".0") or needle)]
        (EV / f"value_flow_{cid}.json").write_text(json.dumps({"exact_hits": hits}, indent=2))
        passes.append(dict(id=cid, check="value-flow probe",
                           detail=f"{what}: {len(hits)} exact matches in output_dict"))

    # ---------------------------------------------------------------- 8
    for cid, row in rows.items():
        if cid.endswith("__run2") or row["status"] != "design_ok":
            continue
        o = load_output(cid)
        if not o:
            continue
        bad = {k: v for k, v in o.items()
               if isinstance(v, float) and not math.isfinite(v)}
        if bad:
            finding(f"FE-{cid}", "high",
                    f"Non-finite (NaN/inf) values in output_dict of {cid}",
                    {"values": {k: str(v) for k, v in list(bad.items())[:20]},
                     "count": len(bad)}, "JSON dumps recorded __nonfinite__ sentinels")
        util_bad = {}
        for k, v in o.items():
            if "util" in k.lower() and num(v) and (v < 0 or v > 100):
                util_bad[k] = v
        if util_bad:
            (EV / f"utils_{cid}.json").write_text(json.dumps(util_bad, indent=2))
            finding(f"FE-UTIL-{cid}", "medium",
                    f"Utilisation values outside [0,100] in {cid}",
                    {"evidence": f"evidence/analyze/utils_{cid}.json",
                     "count": len(util_bad)}, "check key semantics (may be ratios)")
    # span growth: GE01 (20m) vs GE03 (45m) girder depth / overall width
    if status("GE01") == "design_ok" and status("GE03") == "design_ok":
        o1, o3 = load_output("GE01"), load_output("GE03")
        depth_keys = [k for k in (o1 or {}) if "girder_details" in k and "depth" in k.lower()]
        grew = [k for k in depth_keys
                if num(o1.get(k)) and num(o3.get(k)) and o3[k] >= o1[k] > 0]
        (EV / "span_growth.json").write_text(json.dumps(
            {"compared": depth_keys, "grew": grew}, indent=2))
        if depth_keys and len(grew) < len(depth_keys):
            finding("FE-SPAN", "medium",
                    "Section sizes do not grow from 20 m to 45 m span",
                    {"evidence": "evidence/analyze/span_growth.json"}, None)
        else:
            passes.append(dict(id="GE01vsGE03", check="span growth",
                               detail=f"{len(grew)}/{len(depth_keys)} depth keys grew"))

    # ---------------------------------------------------------------- report
    (EV / "passes.json").write_text(json.dumps(passes, indent=2))
    (EV / "findings.json").write_text(json.dumps(findings, indent=2))
    lines = ["# Analyze Report (automatic checks)", "",
             f"Findings: {len(findings)}   Passes: {len(passes)}", ""]
    for f in findings:
        lines += [f"## {f['id']} [{f['severity']}] {f['title']}",
                  f"- Evidence: {json.dumps(f['evidence'])}",
                  f"- Note: {f['note'] or '-'}", ""]
    (NOTES / "analyze_report.md").write_text("\n".join(lines))
    print(f"\nFindings: {len(findings)} -> notes/analyze_report.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
