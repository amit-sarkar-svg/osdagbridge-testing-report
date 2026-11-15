#!/usr/bin/env python3
"""Fetch ALL issues (open+closed, PRs excluded) from Nidhikhare12/OsdagBridge via gh api.

Usage:
    python scripts/fetch_issues_gh.py            # fetch and write notes/issues_raw.json + notes/existing_issues.md
    python scripts/fetch_issues_gh.py --dry-run  # print page stats only, write nothing
    python scripts/fetch_issues_gh.py --help
"""
import argparse
import datetime
import json
import subprocess
import sys
from pathlib import Path

REPO = "Nidhikhare12/OsdagBridge"
ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "notes" / "issues_raw.json"
INDEX = ROOT / "notes" / "existing_issues.md"


def gh_api(url: str):
    out = subprocess.run(["gh", "api", url], capture_output=True, text=True)
    if out.returncode != 0:
        sys.exit(f"gh api failed for {url}:\n{out.stderr.strip()}")
    return json.loads(out.stdout)


def fetch(dry_run: bool):
    items, page = [], 1
    while True:
        batch = gh_api(f"repos/{REPO}/issues?state=all&per_page=100&page={page}")
        print(f"page {page}: {len(batch)} items")
        if not batch:
            break
        items.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    issues = [i for i in items if "pull_request" not in i]
    prs = len(items) - len(issues)
    print(f"total items={len(items)}  PRs skipped={prs}  issues={len(issues)}")
    if dry_run:
        return issues
    RAW.write_text(json.dumps({"fetched_at": datetime.datetime.now().isoformat(timespec="seconds"),
                               "repo": REPO, "items": items}, indent=1))
    lines = [f"# Existing issues {REPO} (open+closed, PRs excluded)",
             f"Fetched {datetime.datetime.now():%Y-%m-%d %H:%M} via gh api — {len(issues)} issues "
             f"({sum(1 for i in issues if i['state']=='open')} open, "
             f"{sum(1 for i in issues if i['state']=='closed')} closed), {prs} PRs skipped.", ""]
    for i in sorted(issues, key=lambda x: x["number"]):
        labels = ",".join(l["name"] for l in i.get("labels", []))
        title = i["title"].replace("|", "\\|")
        lines.append(f"- #{i['number']} [{i['state']}] {title}"
                     + (f"  `{labels}`" if labels else ""))
    INDEX.write_text("\n".join(lines) + "\n")
    print(f"wrote {RAW} and {INDEX}")
    return issues


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true", help="fetch and report counts without writing files")
    args = ap.parse_args()
    fetch(args.dry_run)


if __name__ == "__main__":
    main()
