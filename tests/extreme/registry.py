# Extreme-test case registry.
# Each case = dict(id, layer, kind, fn (returns input dict or writes input file),
# oracle (callable(input, layer)->None or raises), expect, timeout, tags)
# Oracles are ORACES, defined in oracle.py and passed via fn_name.
from __future__ import annotations

CASES: list[dict] = []


def register(id, layer, oracle, fn, expect=None, timeout=600, tags=()):
    CASES.append(dict(id=id, layer=layer, oracle=oracle, fn=fn,
                      expect=expect, timeout=timeout, tags=tuple(tags)))


def filter_cases(layer=None, tags=(), ids=None, dry=False):
    out = []
    for c in CASES:
        if layer and c["layer"] not in set(layer.split(",")):
            continue
        if tags and not (set(c["tags"]) & set(tags)):
            continue
        if ids and c["id"] not in ids:
            continue
        out.append(c)
    return out


def dump():
    for c in CASES:
        print(f"{c['id']}\t{c['layer']}\t{c['oracle']}\t{','.join(c['tags'])}")
