#!/usr/bin/env python3
"""Search FULL issue titles and bodies in notes/issues_raw.json.

Usage:
  python scripts/search_issues.py keyword [keyword...]
  python scripts/search_issues.py --and kw1 kw2   # all must match (case-insensitive)

Prints: #num [state] title  and matching line(s) (capped).
"""
import argparse, json, re, sys
from pathlib import Path

RAW = Path(__file__).resolve().parent.parent / "notes/issues_raw.json"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--and", dest="and_mode", action="store_true", help="require all keywords")
    ap.add_argument("--context", type=int, default=0, help="not used; kept for compat")
    ap.add_argument("keywords", nargs="+")
    args = ap.parse_args()
    data = json.load(open(RAW))
    items = [i for i in data.get("items", []) if "pull_request" not in i]
    kws = [k.lower() for k in args.keywords]
    hits = 0
    for it in sorted(items, key=lambda x: x["number"]):
        title = it.get("title") or ""
        body = it.get("body") or ""
        blob = (title + "\n" + body).lower()
        if args.and_mode:
            ok = all(k in blob for k in kws)
        else:
            ok = any(k in blob for k in kws)
        if not ok:
            continue
        hits += 1
        print(f"#{it['number']} [{it['state']}] {title}")
        # show matching lines
        shown = 0
        for ln in (title + "\n" + body).splitlines():
            l = ln.lower()
            if any(k in l for k in kws):
                s = ln.strip()
                if len(s) > 220:
                    s = s[:217] + "..."
                print(f"  > {s}")
                shown += 1
                if shown >= 4:
                    break
        if shown == 0:
            print("  > (match in body)")
    if hits == 0:
        print("NO_MATCH")
    else:
        print(f"--- {hits} issue(s) ---")


if __name__ == "__main__":
    main()
