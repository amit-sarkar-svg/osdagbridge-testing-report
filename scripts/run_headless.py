#!/usr/bin/env python
"""Orchestrate headless runs of the generated cases.

Each case runs in its own subprocess with a timeout (default 600 s), so one
hang never blocks the rest. Sequential by default (designs are slow and
memory-heavy).

Usage:
  python run_headless.py --dry-run            # first 3 cases only
  python run_headless.py                      # all cases in manifest
  python run_headless.py --only GE01,GE02
  python run_headless.py --rerun SN01         # rerun into <case>__run2 for determinism
"""
from __future__ import annotations

import argparse
import csv
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "scripts"
GEN = REPO / "test_cases" / "generated"
MANIFEST = REPO / "test_cases" / "manifest.json"
RESULTS = REPO / "test_cases" / "results.csv"
DICTS = REPO / "dictionaries"

CSV_FIELDS = [
    "id", "area", "expect", "status", "validator_valid", "validator_errors",
    "solve", "prime", "design_exception_type", "runtime_s", "design_runtime_s", "out_dir",
]


def run_case(case: dict, timeout: int, suffix: str = "", prime_mode: str = "osi_load") -> dict:
    cid = case["id"] + suffix
    out_dir = DICTS / cid
    out_dir.mkdir(parents=True, exist_ok=True)
    log_path = out_dir / "case.log"
    cmd = [sys.executable, str(SCRIPTS / "case_runner.py"), str(REPO / case["file"]), str(out_dir),
           f"--prime-mode={prime_mode}"]
    row = {
        "id": cid,
        "area": case["area"],
        "expect": case["expect"],
        "status": "no_result",
        "validator_valid": "",
        "validator_errors": "",
        "solve": "",
        "prime": prime_mode,
        "design_exception_type": "",
        "runtime_s": "",
        "design_runtime_s": "",
        "out_dir": str(out_dir.relative_to(REPO)),
    }
    t0 = time.time()
    try:
        with log_path.open("w") as log:
            proc = subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT, timeout=timeout)
    except subprocess.TimeoutExpired:
        row["status"] = "timeout"
        row["runtime_s"] = round(time.time() - t0, 1)
        with log_path.open("a") as log:
            log.write(f"\n[run_headless] TIMEOUT after {timeout}s, killed\n")
        return row

    rj = out_dir / "result.json"
    if rj.exists():
        import json
        r = json.loads(rj.read_text())
        row["status"] = r.get("status", "unknown")
        row["validator_valid"] = r.get("validator_valid", "")
        row["validator_errors"] = r.get("validator_errors", "")
        row["solve"] = r.get("solve", "skipped" if "--no-solve" in cmd else "")
        row["prime"] = r.get("prime", prime_mode)
        row["design_exception_type"] = r.get("design_exception_type", "")
        row["runtime_s"] = r.get("runtime_s", round(time.time() - t0, 1))
        row["design_runtime_s"] = r.get("design_runtime_s", "")
    else:
        row["status"] = f"crashed(exit={proc.returncode})"
    return row


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="run only the first 3 cases")
    ap.add_argument("--only", help="comma-separated case ids")
    ap.add_argument("--rerun", help="case id to re-run with __run2 suffix (determinism)")
    ap.add_argument("--prime-mode", choices=["osi_load", "in_session"], default="osi_load",
                    help="material priming emulation mode (see ui_emulation.py)")
    ap.add_argument("--timeout", type=int, default=600)
    ap.add_argument("--append", action="store_true", help="append to results.csv instead of rewrite")
    args = ap.parse_args()

    if not MANIFEST.exists():
        print("manifest.json missing - run gen_cases.py first", file=sys.stderr)
        return 2

    import json
    cases = json.loads(MANIFEST.read_text())
    if args.only:
        wanted = [s.strip() for s in args.only.split(",")]
        cases = [c for c in cases if c["id"] in wanted]
    if args.dry_run:
        cases = cases[:3]
        print(f"DRY RUN: {len(cases)} cases")

    rows = []
    if args.rerun:
        match = [c for c in json.loads(MANIFEST.read_text()) if c["id"] == args.rerun]
        if not match:
            print(f"case {args.rerun} not in manifest", file=sys.stderr)
            return 2
        rows.append(run_case(match[0], args.timeout, suffix="__run2", prime_mode=args.prime_mode))
    else:
        for i, case in enumerate(cases, 1):
            print(f"[{i}/{len(cases)}] {case['id']}: {case['desc']}", flush=True)
            rows.append(run_case(case, args.timeout, prime_mode=args.prime_mode))

    mode = "a" if args.append else "w"
    new_file = not RESULTS.exists() or not args.append
    with RESULTS.open(mode, newline="") as f:
        w = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        if new_file:
            w.writeheader()
        for r in rows:
            print(f"  -> {r['id']}: {r['status']} ({r['runtime_s']}s)")
            w.writerow(r)
    print(f"results -> {RESULTS}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
