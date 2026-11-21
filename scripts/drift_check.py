#!/usr/bin/env python3
import sys, os, math, re
CLONE = "/Users/macbook/Projects/OsdagBridge/src"
sys.path.insert(0, CLONE)

from osdagbridge.core.bridge_types.plate_girder.validator import BridgeInputValidator
from osdagbridge.core.utils.osi_validator import OsiInputValidator, _BASIC_KEYS, _ADDITIONAL_KEYS, _VALID_DESIGN_MODES
from osdagbridge.core.utils import common as C

bv = BridgeInputValidator()
ov = OsiInputValidator()

def line(s=""): print(s)

# --- helpers ---
def check_basic(key, val, extra=None):
    inp = {key: val}
    if extra: inp.update(extra)
    return bv.validate_basic_inputs(key, inp)

def check_add(key, val, extra=None):
    inp = {key: val}
    if extra: inp.update(extra)
    return bv.validate_additional_inputs(key, inp)

def check_mat(key, val):
    return bv.validate_material_inputs(key, {key: val})

# 1) Specific: material inputs branch for cross-bracing/end-diaphragm/stiffener Fy=5000
line("== MATERIAL COMPONENT FY=5000 (validate_material_inputs) ==")
mat_fy_keys = [
    ("girder_fy", C.KEY_MATERIAL_GIRDER_FY),
    ("cross_bracing_fy", C.KEY_MATERIAL_CROSS_BRACING_FY),
    ("end_diaphragm_fy", C.KEY_MATERIAL_END_DIAPHRAGM_FY),
]
for name,k in mat_fy_keys:
    r = check_mat(k, 5000)
    line(f"{name} ({k}): {('REJECTED -> '+str(r)) if r else 'ACCEPTED (None)'}")
# also check other CB/ED props to see if any branch exists
cb_ed_samples = [
    (C.KEY_MATERIAL_CROSS_BRACING_FU, 2000), (C.KEY_MATERIAL_CROSS_BRACING_E, 500),
    (C.KEY_MATERIAL_CROSS_BRACING_DENSITY, 200),
    (C.KEY_MATERIAL_END_DIAPHRAGM_FU, 2000), (C.KEY_MATERIAL_END_DIAPHRAGM_DENSITY, 200),
]
line("-- CB/ED other props samples --")
for k,v in cb_ed_samples:
    r = check_mat(k,v)
    line(f"{k}={v}: {('REJECTED') if r else 'ACCEPTED'}")
# stiffener material keys? search in common
stiff_mat = [n for n in dir(C) if 'STIFFENER' in n and 'MATERIAL' in n]
line(f"stiffener material keys in common: {stiff_mat}")

# 2) Enum/unknown values accepted by osi_validator?
line("\n== ENUM/UNKNOWN in osi_validator ==")
cases = {
    "design.mode unknown": {"design.mode": "Banana"},
    "structure.type unknown": {"structure.type": "Railway Bridge"},
    "geometry.include_median unknown": {"geometry.include_median": "Maybe"},
    "geometry.footpath unknown": {"geometry.footpath": "Triple"},
}
for name,data in cases.items():
    res = ov.validate(data)
    line(f"{name}: valid={res.is_valid} errors={res.errors[:2]}")

# median Yes with carriageway below 7.5
line("\n== CROSS-FIELD: median Yes, carriageway < 7.5 ==")
# basic validator
r = bv.validate_basic_inputs(C.KEY_CARRIAGEWAY_WIDTH, {C.KEY_CARRIAGEWAY_WIDTH: 6.0, C.KEY_INCLUDE_MEDIAN: "Yes"})
line(f"validate_basic_inputs cw=6.0 median=Yes: {r}")
# osi_validator at load time (present values)
res = ov.validate({C.KEY_CARRIAGEWAY_WIDTH: 6.0, C.KEY_INCLUDE_MEDIAN: "Yes", C.KEY_SPAN: 30.0})
line(f"osi_validator load cw=6.0 median=Yes span=30: valid={res.is_valid} errors={res.errors}")

# 3) Compact table key | L1(core validator) | L2(osi_validator enforced) | L3(UI grep) | agree?
# Build L2 presence: in _BASIC_KEYS or _ADDITIONAL_KEYS; material keys absent from osi lists
def osi_enforces(key):
    if key in _BASIC_KEYS: return "basic"
    if key in _ADDITIONAL_KEYS: return "additional"
    if key == "design.mode": return "enum(mode)"
    return "no"

# L3 quick grep in UI for a key fragment
ui_root = "/Users/macbook/Projects/OsdagBridge/src/osdagbridge/desktop/ui"
def ui_mentions(key):
    # search for last token or key string occurrences
    frag = key.split('.')[-1]
    try:
        import subprocess
        out = subprocess.check_output(["grep","-RIn",frag,ui_root], text=True, stderr=subprocess.DEVNULL)
        lines = out.strip().splitlines()
        return len(lines)
    except Exception:
        return 0

rows = []
# basic
for key in _BASIC_KEYS:
    rows.append((key, "basic()", osi_enforces(key)))
# some additional keys sample including those in _ADDITIONAL_KEYS and some material keys
sample_add = list(_ADDITIONAL_KEYS)[:12]
for key in sample_add:
    rows.append((key, "additional()", osi_enforces(key)))
# material keys - girder and cb/ed
mat_keys = [C.KEY_MATERIAL_GIRDER_FY, C.KEY_MATERIAL_GIRDER_DENSITY, C.KEY_MATERIAL_DECK_FCK,
            C.KEY_MATERIAL_CROSS_BRACING_FY, C.KEY_MATERIAL_END_DIAPHRAGM_FY, C.KEY_MATERIAL_DECK_DENSITY]
for key in mat_keys:
    rows.append((key, "material()", osi_enforces(key)))
rows.append(("design.mode","N/A",osi_enforces("design.mode")))
rows.append(("structure.type","N/A (enum in UI/common)","no"))
rows.append(("geometry.include_median","N/A","no"))

line("\n== COMPACT TABLE (key | L1 | L2_osi | L3_ui_mentions | agree?) ==")
line("key | L1 | L2_osi | L3_ui_hits | agree?")
for key,l1,l2 in rows[:40]:
    l3 = ui_mentions(key)
    agree = "Y" if (l2!="no" and l1 not in ("N/A","N/A (enum in UI/common)")) or (l2=="no" and l1.startswith("N/A")) or (l2=="no" and "material" in l1) else ("PARTIAL" if l2!="no" else "N")
    # better agree logic: osi enforces same category as validator exists?
    if "material" in l1 and l2=="no": agree="N (osi skips)"
    elif l1=="additional()" and l2=="additional": agree="Y (present-only)"
    elif l1=="basic()" and l2=="basic": agree="Y (present-only)"
    elif l2.startswith("enum"): agree="Y (mode only)"
    line(f"{key} | {l1} | {l2} | {l3} | {agree}")

# 4) keys in _ADDITIONAL_KEYS: have limit in osi_validator but different limit (or none) in validate_additional_inputs?
# osi_validator calls validate_additional_inputs for each - so "limit in osi_validator but different in validate_additional_inputs" means?
# probably osi_validator's notion (it just delegates) vs core limits. But request states "limit in osi_validator but a different limit (or none) in validate_additional_inputs"
# We'll test: for each key in _ADDITIONAL_KEYS, try extreme value and see if validator returns correction (has limit) or None (no limit) 
line("\n== _ADDITIONAL_KEYS: validate_additional_inputs response to extreme value ==")
extreme_results = []
for key in _ADDITIONAL_KEYS:
    try:
        r = check_add(key, 10**9)
        r2 = check_add(key, -10**9)
        has = (r is not None) or (r2 is not None)
        extreme_results.append((key, has, r, r2))
    except Exception as e:
        extreme_results.append((key, 'ERR', str(e), None))
none_keys = [k for k,has,_,_ in extreme_results if has==False]
has_keys = [k for k,has,_,_ in extreme_results if has==True]
err_keys = [k for k,has,_,_ in extreme_results if has=='ERR']
line(f"total={len(_ADDITIONAL_KEYS)} with_limit_response={len(has_keys)} no_limit_response={len(none_keys)} err={len(err_keys)}")
line("no_limit_response keys (first 20): " + ", ".join(none_keys[:20]))
line("err keys: " + ", ".join(err_keys[:10]))
# show a few examples
for k,has,r,r2 in extreme_results[:10]:
    line(f"  ex {k}: high={r} low={r2}")
