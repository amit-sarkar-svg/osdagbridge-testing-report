#!/usr/bin/env python3
"""Area 1 key map: which input-dictionary keys does the core actually read?

Loads a full solved input dictionary (default: the probe input saved by
scripts/pipeline_probe.py), then searches the core source tree for each key
literal. Keys that never appear outside defaults/ui_fields are reported as
possible dead inputs. Also reports KEY_* constants defined in common.py whose
value is absent from the solved dictionary (core expects a key the UI pipeline
never writes).

Usage:
    python scripts/area1_keymap.py [--input PATH] [--dry-run] [--help]
"""
import argparse
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CLONE = Path("/Users/macbook/Projects/OsdagBridge")
DEFAULT_INPUT = ROOT / "evidence" / "pipeline_probe" / "probe_input.yaml"
CORE = CLONE / "src" / "osdagbridge" / "core"
SKIP_FILES = {
    "defaults.py", "ui_fields.py", "ui_fields_additional_input.py",
    "ui_fields_project_location.py", "common.py",
}


def core_sources():
    for p in CORE.rglob("*.py"):
        if p.name in SKIP_FILES or "__pycache__" in p.parts:
            continue
        yield p, p.read_text(errors="ignore")


def key_constants():
    text = (CORE / "utils" / "common.py").read_text(errors="ignore")
    return dict(re.findall(r'^(KEY_[A-Z0-9_]+)\s*=\s*"([^"]+)"', text, re.M))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input", default=str(DEFAULT_INPUT), help="solved input dictionary YAML")
    ap.add_argument("--dry-run", action="store_true", help="report counts only")
    ap.add_argument("--out", default=str(ROOT / "notes" / "area1_keymap.txt"))
    args = ap.parse_args()

    if not Path(args.input).exists():
        sys.exit(f"missing input dictionary: {args.input} (run scripts/pipeline_probe.py first)")
    data = yaml.safe_load(open(args.input))
    keys = sorted(k for k in data if isinstance(k, str))
    sources = list(core_sources()) if not args.dry_run else []
    print(f"input keys: {len(keys)}  core files scanned: {len(sources) if not args.dry_run else 'dry-run'}")

    if args.dry_run:
        return

    consts = key_constants()
    const_by_value = {}
    for name, val in consts.items():
        const_by_value.setdefault(val, []).append(name)

    dead = []
    for k in keys:
        needles = [f'"{k}"', f"'{k}'"] + const_by_value.get(k, [])
        if not any(n in t for _, t in sources for n in needles):
            dead.append(k)

    missing = {name: val for name, val in consts.items() if val not in data and val.startswith(("geometry.", "material.", "typical_section.", "design_options"))}

    lines = [f"# Area 1 key map — input: {args.input}",
             f"# solved input keys: {len(keys)}; core files scanned: {len(sources)}", "",
             f"## Keys with no literal read in core/ ({len(dead)})",
             "(appear only in defaults/ui_fields or nowhere — candidate dead inputs)", ""]
    lines += [f"- {k} = {data[k]!r}" for k in dead]
    lines += ["", f"## common.py KEY_* values absent from the solved dictionary ({len(missing)})",
              "(core constant defined but the UI/default pipeline never writes that key)", ""]
    lines += [f"- {n} = {v}" for n, v in sorted(missing.items())]
    Path(args.out).write_text("\n".join(lines) + "\n")
    print(f"dead-input candidates: {len(dead)}; constants absent from solved dict: {len(missing)}")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
