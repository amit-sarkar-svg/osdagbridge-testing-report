#!/usr/bin/env python3
"""Keyword search over issue titles AND bodies in notes/issues_raw.json.
Usage: python3 scripts/search_issues.py <keyword> [keyword2 ...]
Prints: number, title, matching line(s)."""
import json, sys, re
path = "notes/issues_raw.json"
if len(sys.argv) < 2:
    print("usage: search_issues.py <keyword> [...]"); sys.exit(1)
try:
    data = json.load(open(path))
except Exception as e:
    print("error loading", path, e); sys.exit(1)
keys = [k.lower() for k in sys.argv[1:]]
for it in data:
    if "pull_request" in it: 
        continue
    num = it.get("number"); title = it.get("title") or ""; body = it.get("body") or ""
    hay = (title + "\n" + body)
    hayl = hay.lower()
    if not all(k in hayl for k in keys):
        continue
    print(f"#{num} [{it.get('state')}] {title}")
    for i,line in enumerate(hay.splitlines(),1):
        ll = line.lower()
        if any(k in ll for k in keys):
            s = line.strip()
            if len(s)>200: s=s[:200]+"..."
            print(f"  L{i}: {s}")
    print("---")
