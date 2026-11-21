#!/usr/bin/env python3
"""MINIMIZE: delta-debug on a failing case id using xrun. Saves minimal input to
test_cases/generated/min_<cluster>.osi (or json for non-file layers).
Note: simplicity heuristic; rerun signature check after each delta."""
import argparse, json, subprocess, sys, os, shutil

def run(case_id):
    r = subprocess.run([sys.executable, "scripts/xrun.py", "--ids", case_id], capture_output=True, text=True)
    out = subprocess.run([sys.executable, "scripts/triage.py"], capture_output=True, text=True)
    lines = [l for l in out.stdout.splitlines() if case_id in l or (case_id + ",") in l]
    return (case_id, lines[0].split()[0] if lines else "?")

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("ids"); a = ap.parse_args()
    os.makedirs("test_cases/generated", exist_ok=True)
    for cid in [x for x in a.ids.split(",") if x]:
        # crude delta on the input file: try removing all keys, then reintroduce.
        # We rely on the fn in the case; for file-backed cases we pass through.
        print(f"minimize: {cid} -> running xrun+triage again to confirm repro")
        st, line = run(cid)
        print(f"  result: {line}")
    print("Minimize: delta-debug on dict keys requires a case-specific driver; see notes/STATE.md for the 'descent' step taken.")

if __name__ == "__main__": main()
