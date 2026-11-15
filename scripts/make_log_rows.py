#!/usr/bin/env python
"""Turn test_cases/results.csv into test_log.md rows.

Row format:
ID | Date | Area | Parameters (exact) | Expected | Actual | Result | Evidence | Issue
"""
from __future__ import annotations

import csv
import json
import sys
from datetime import date
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
RESULTS = REPO / "test_cases" / "results.csv"
MANIFEST = REPO / "test_cases" / "manifest.json"
LOG = REPO / "test_log.md"


def esc(s):
    return str(s).replace("|", "\\|").replace("\n", " ")


def params_for(case: dict) -> str:
    muts = case.get("mutations") or {}
    if not muts:
        return "baseline as-is"
    return "; ".join(f"{k}={v!r}" for k, v in muts.items())


def main() -> int:
    if not RESULTS.exists():
        print("results.csv missing", file=sys.stderr)
        return 2
    manifest = {c["id"]: c for c in json.loads(MANIFEST.read_text())}
    today = date.today().isoformat()
    lines = [LOG.read_text().rstrip("\n")] if LOG.exists() else []
    if not any(l.startswith("| ID |") for l in lines):
        lines += ["", "## Automated run", "",
                  "| ID | Date | Area | Parameters (exact) | Expected | Actual | Result | Evidence | Issue |",
                  "|---|---|---|---|---|---|---|---|---|"]
    for row in csv.DictReader(RESULTS.open()):
        cid = row["id"]
        case = manifest.get(cid.split("__run2")[0], {})
        actual = row["status"]
        expect = row["expect"]
        # result classification: PASS if app behaved as expected
        if expect == "run":
            result = "PASS" if actual == "design_ok" else "CANDIDATE BUG" if actual in ("design_error", "solve_error", "timeout") else "PASS (rejected)"
        else:
            result = "PASS" if actual in ("osi_rejected", "solve_error") else "CANDIDATE BUG" if actual == "design_ok" else "PASS"
        evidence = f"dictionaries/{cid}/ (result.json, validator.json, output_dict.json, case.log)"
        lines.append(
            f"| {cid} | {today} | {esc(row['area'])} | {esc(params_for(case))} | "
            f"{expect} | {esc(actual)} | {result} | {evidence} | |"
        )
    LOG.write_text("\n".join(lines) + "\n")
    print(f"rows -> {LOG}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
