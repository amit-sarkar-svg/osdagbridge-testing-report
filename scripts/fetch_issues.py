#!/usr/bin/env python
"""Fetch all issues (open + closed, excluding PRs) from the OsdagBridge repo.

Writes:
  notes/issues_raw.json     - raw JSON list
  notes/existing_issues.md  - readable index (number, title, state, labels)

Exits non-zero if the network call fails so the caller knows the duplicate
check is unavailable.
"""
from __future__ import annotations

import json
import sys
import urllib.request
from pathlib import Path

REPO = "Nidhikhare12/OsdagBridge"
ROOT = Path(__file__).resolve().parents[1]
NOTES = ROOT / "notes"
RAW = NOTES / "issues_raw.json"
MD = NOTES / "existing_issues.md"


def fetch_all() -> list[dict]:
    issues: list[dict] = []
    page = 1
    while True:
        url = f"https://api.github.com/repos/{REPO}/issues?state=all&per_page=100&page={page}"
        with urllib.request.urlopen(url, timeout=60) as resp:
            batch = json.load(resp)
        if not batch:
            break
        issues.extend(batch)
        print(f"page {page}: {len(batch)} item(s)")
        page += 1
    # Skip PRs
    return [i for i in issues if "pull_request" not in i]


def main() -> int:
    NOTES.mkdir(exist_ok=True)
    try:
        issues = fetch_all()
    except Exception as exc:
        print(f"NETWORK ERROR: could not fetch issues: {exc}", file=sys.stderr)
        return 1

    RAW.write_text(json.dumps(issues, indent=2))
    lines = ["# Existing OsdagBridge Issues (open + closed, PRs excluded)", "",
             f"Total: {len(issues)}", "",
             "| # | State | Title | Labels |", "|---|-------|-------|--------|"]
    for i in sorted(issues, key=lambda x: x["number"]):
        labels = ", ".join(l["name"] for l in i.get("labels", []))
        lines.append(f"| #{i['number']} | {i['state']} | {i['title']} | {labels} |")
    MD.write_text("\n".join(lines) + "\n")
    print(f"Saved {len(issues)} issues -> {RAW}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
