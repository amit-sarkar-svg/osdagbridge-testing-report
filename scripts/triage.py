#!/usr/bin/env python3
"""TRIAGE: cluster xrun failures by (exception_type, innermost OsdagBridge frame,
message template with numbers masked). Prints one row per cluster."""
import argparse, json, re, collections, subprocess, sys, os

def normalize(s):
    s = re.sub(r"0x[0-9a-fA-F]+", "0xADDR", s)
    s = re.sub(r"\b\d+\.?\d*([eE][+-]?\d+)?\b", "NUM", s)
    return re.sub(r"\s+", " ", s.strip())[:120]

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--input", "--in", dest="input_file", default="evidence/xrun/results.jsonl")
    ap.add_argument("--mask-zero-runtime", action="store_true"); a = ap.parse_args()
    rows = [json.loads(l) for l in open(a.input_file)]
    clusters = collections.OrderedDict()
    for r in rows:
        key = (r["status"], r["exception_type"], r["innermost_frame"], normalize(r["traceback_sig"]) or r["message"])
        clusters.setdefault(key, []).append(r)
    print(f"rows={len(rows)} clusters={len(clusters)}")
    for i, (key, rs) in enumerate(sorted(clusters.items(), key=lambda kv: -len(kv[1])), 1):
        st, et, frame, msg = key
        issue = "NEW"
        if st in ("PASS",):
            print(f"[cluster {i}] ({len(rs)}x) PASS {rs[0]['id']}"); continue
        raw = subprocess.run(["grep", "-rlm1", frame or "", "/Users/macbook/Projects/OsdagBridge/src"],
                             capture_output=True, text=True)
        print(f"[cluster {i}] ({len(rs)}x) {st} {et} :: {frame or '(no osdagbridge frame)'} :: {msg[:80]}")
        print(f"           ids: {', '.join(x['id'] for x in rs[:5])}{' ...' if len(rs)>5 else ''}")
        print(f"           inputs: {', '.join(x['input_file'] or '(none)' for x in rs[:3])}")
    return 0

if __name__ == "__main__": sys.exit(main())
