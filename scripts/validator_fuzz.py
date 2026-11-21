#!/usr/bin/env python3
import sys, json, math, traceback
sys.path.insert(0, '/Users/macbook/Projects/OsdagBridge/src')
from osdagbridge.core.bridge_types.plate_girder.validator import BridgeInputValidator
from osdagbridge.core.utils import common as C

bv = BridgeInputValidator()

# values to test
vals = [None, "", "  ", "abc", "1e400", "30,5", "30 m", True, False, [], {}, -0.0, float('nan'), float('inf'), float('-inf'), 1e308, "١٢"]
# add string/number forms of some common limits
extra = ["0","0.0","20","20.0","45","45.0","4.25","23.6","-15","15","100","1200","1500","300","120","0.5","1","30","18","28","10","80","6","50"]
for e in extra:
    if e not in vals: vals.append(e)
    try:
        n=float(e); 
        if n not in vals: vals.append(n)
    except: pass

basic_keys = [C.KEY_SPAN, C.KEY_CARRIAGEWAY_WIDTH, C.KEY_SKEW_ANGLE]
material_keys = [
    C.KEY_MATERIAL_GIRDER_DENSITY, C.KEY_MATERIAL_GIRDER_FY, C.KEY_MATERIAL_GIRDER_FU,
    C.KEY_MATERIAL_GIRDER_E, C.KEY_MATERIAL_GIRDER_G, C.KEY_MATERIAL_GIRDER_POISSON, C.KEY_MATERIAL_GIRDER_THERMAL,
    C.KEY_MATERIAL_DECK_DENSITY, C.KEY_MATERIAL_DECK_FCK, C.KEY_MATERIAL_DECK_FCTM, C.KEY_MATERIAL_DECK_ECM, C.KEY_MATERIAL_DECK_THERMAL,
]
# additional keys - resolve from validator branches by trying constants present
add_keys = []
# collect all KEY_* in common that look relevant? easier: use known list from grep
add_const_names = [
 'KEY_TS_GIRDER_SPACING','KEY_TS_NO_OF_GIRDERS','KEY_TS_DECK_OVERHANG','KEY_TS_DECK_THICKNESS','KEY_TS_FOOTPATH_WIDTH','KEY_TS_FOOTPATH_THICKNESS',
 'KEY_CB_WIDTH','KEY_CB_HEIGHT','KEY_CB_LOAD','KEY_CB_POST_SPACING','KEY_MD_WIDTH','KEY_MD_HEIGHT','KEY_MD_LOAD','KEY_MD_POST_SPACING',
 'KEY_RL_HEIGHT','KEY_RL_WIDTH','KEY_RL_LOAD_VALUE','KEY_WC_DENSITY','KEY_WC_THICKNESS','KEY_WC_LD_LANE_TABLE_COUNT','KEY_WC_LD_LANE_TABLE',
 'KEY_MP_GD_SUPPORT_WIDTH','KEY_MP_GIRDER_DEPTH','KEY_MP_GIRDER_TOP_FLANGE_WIDTH','KEY_MP_GIRDER_BOTTOM_FLANGE_WIDTH',
 'KEY_MP_GIRDER_TOP_FLANGE_THICKNESS','KEY_MP_GIRDER_BOTTOM_FLANGE_THICKNESS','KEY_MP_GIRDER_WEB_THICKNESS',
 'KEY_MP_STIFFENER_SPACING','KEY_MP_STIFFENER_BEARING_OUTSTAND','KEY_MP_STIFFENER_INTERMEDIATE_SPACING','KEY_MP_STIFFENER_INTERMEDIATE_OUTSTAND',
 'KEY_MP_CB_NO_OF_CROSS_BRACINGS','KEY_PL_SELF_WEIGHT_FACTOR','KEY_LL_ECCENTRICITY','KEY_LL_FOOTPATH_PRESSURE_VALUE',
 'KEY_SL_IMPORTANCE_FACTOR','KEY_SL_TIME_PERIOD','KEY_SL_DAMPING','KEY_SL_DEAD_LOAD_VALUE','KEY_SL_LIVE_LOAD_VALUE',
 'KEY_WL_AVG_EXPOSED_HEIGHT','KEY_WL_GUST_FACTOR_VALUE','KEY_WL_DRAG_COEFF_VALUE','KEY_WL_DRAG_COEFF_LL_VALUE','KEY_WL_LIFT_COEFF_VALUE',
 'KEY_WL_SUPER_AREA_ELEV_VALUE','KEY_WL_SUPER_AREA_PLAIN_VALUE','KEY_WL_EXPOSED_FRONTAL_VALUE','KEY_WL_WIND_ECC_DECK_VALUE','KEY_WL_WIND_LL_ECC_VALUE',
 'KEY_TL_THERMAL_COEFF_STEEL','KEY_TL_THERMAL_COEFF_RCC','KEY_DS_REINF_BOUNDS','KEY_DS_TOP_CLEAR_COVER','KEY_DS_BOTTOM_CLEAR_COVER','KEY_DS_SIDE_CLEAR_COVER',
 'KEY_DS_STUD_YIELD_STRENGTH','KEY_DS_STUD_ULTIMATE_STRENGTH','KEY_DS_STUD_HEIGHT','KEY_DS_STUD_COUNT','KEY_DS_STUD_TRANSVERSE_SPACING',
 'KEY_DO_GAMMA_C_BASIC','KEY_DO_GAMMA_C_ACCIDENTAL','KEY_DO_GAMMA_M0','KEY_DO_GAMMA_M1','KEY_DO_GAMMA_S','KEY_DO_GAMMA_V','KEY_DO_GAMMA_FLT','KEY_DO_GAMMA_MF',
 'KEY_DO_LOAD_CYCLES','KEY_DO_CAMBER_VALUE'
]
for n in add_const_names:
    if hasattr(C,n): add_keys.append(getattr(C,n))
# plus string-key branches in additional
add_keys += [
  "member_properties.girder_details.segment_chain",
  "member_properties.end_diaphragm_details.welded_beam.depth",
  "member_properties.end_diaphragm_details.welded_beam.top_flange_width",
  "member_properties.end_diaphragm_details.welded_beam.bottom_flange_width",
]

def safe_call(fn, key, inp):
    try:
        r = fn(key, inp)
        return ('ok', r)
    except Exception as e:
        return ('exc', f"{type(e).__name__}: {e}")

results = []
flags = []
def record(group, key, val, status, ret):
    rec = {"g":group,"k":key,"v":repr(val),"s":status,"r":repr(ret)}
    results.append(rec)

# test
for key in basic_keys:
    extra_inp = {}
    if key == C.KEY_CARRIAGEWAY_WIDTH:
        extra_inp[C.KEY_INCLUDE_MEDIAN] = "No"
    for v in vals:
        st,ret = safe_call(bv.validate_basic_inputs, key, {key:v, **extra_inp})
        record('basic',key,v,st,ret)
        # flags
        if st=='exc': flags.append(('exc','basic',key,v,ret))
        if st=='ok' and ret is None:
            if isinstance(v,float) and (math.isnan(v) or math.isinf(v)): flags.append(('naninf_valid','basic',key,v,ret))
            if isinstance(v,bool): flags.append(('bool_valid','basic',key,v,ret))
        # "30" vs 30 difference
        if v=="30":
            stn,retn=safe_call(bv.validate_basic_inputs,key,{key:30,**extra_inp})
            if (st,repr(ret))!=(stn,repr(retn)): flags.append(('str_vs_num_diff','basic',key,'30vs30',(ret,retn)))

for key in material_keys:
    for v in vals:
        st,ret = safe_call(bv.validate_material_inputs, key, {key:v})
        record('material',key,v,st,ret)
        if st=='exc': flags.append(('exc','material',key,v,ret))
        if st=='ok' and ret is None:
            if isinstance(v,float) and (math.isnan(v) or math.isinf(v)): flags.append(('naninf_valid','material',key,v,ret))
            if isinstance(v,bool): flags.append(('bool_valid','material',key,v,ret))
        if v=="30":
            stn,retn=safe_call(bv.validate_material_inputs,key,{key:30})
            if (st,repr(ret))!=(stn,repr(retn)): flags.append(('str_vs_num_diff','material',key,'30vs30',(ret,retn)))

for key in add_keys:
    for v in vals:
        st,ret = safe_call(bv.validate_additional_inputs, key, {key:v})
        record('additional',key,v,st,ret)
        if st=='exc': flags.append(('exc','additional',key,v,ret))
        if st=='ok' and ret is None:
            if isinstance(v,float) and (math.isnan(v) or math.isinf(v)): flags.append(('naninf_valid','additional',key,v,ret))
            if isinstance(v,bool): flags.append(('bool_valid','additional',key,v,ret))
        if v=="30":
            stn,retn=safe_call(bv.validate_additional_inputs,key,{key:30})
            if (st,repr(ret))!=(stn,repr(retn)): flags.append(('str_vs_num_diff','additional',key,'30vs30',(ret,retn)))

# summarize flags
from collections import Counter
c=Counter([f[0] for f in flags])
print('F_SUMMARY keys_basic=%d keys_material=%d keys_additional=%d calls=%d flags=%d' % (len(basic_keys),len(material_keys),len(add_keys),len(results),len(flags)))
print('FLAG_COUNTS', dict(c))
# print up to 20 flag examples
for f in flags[:20]:
    print('FLAG', f[0], f[1], f[2], repr(f[3]), repr(f[4])[:120])
# save details
out={'summary':{'basic':len(basic_keys),'material':len(material_keys),'additional':len(add_keys),'calls':len(results),'flags':len(flags),'flag_counts':dict(c)}, 'flags':[{'t':f[0],'g':f[1],'k':f[2],'v':repr(f[3]),'d':repr(f[4])} for f in flags], 'results_sample':results[:200]}
open('evidence/logs/trackF_validator_fuzz.json','w').write(json.dumps(out, default=str))
print('WROTE evidence/logs/trackF_validator_fuzz.json')
