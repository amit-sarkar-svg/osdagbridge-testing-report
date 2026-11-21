"""Bearing-zone web buckling check (designer.py:1664-1670) vs physical limit (squash load) and vs the program's own
compressive-stress function applied to an unstiffened web strut (r = tw/sqrt(12), KL = 0.7 d as in the code).
Inputs read from a saved design state. usage: probe_web_buckling.py <case_dir>"""
import sys,json,math,inspect
sys.path.insert(0,'/Users/macbook/Projects/OsdagBridge/src')
def main():
    from osdagbridge.core.utils.codes.is800_2007 import IS800_2007
    st=json.load(open(sys.argv[1]+'/state.json')); dr=st['design_results']; od=st['output_dict']
    bs=dr['capacity_details']['bearing_stiffener']; chk=[c for c in dr['checks'] if c['name']=='Brg.Stiff: Web Buckling'][0]
    R=chk['demand']; A=bs['A_wb_mm2']; fcc=bs['fcc_wb_MPa']; fcd_y=bs['fcd_y_MPa']
    tw=float(od['steeldesign.details.web_thickness']); d=float(od['member_properties.girder_details.section_input.web_depth'])*1000
    gm0=1.1; fy=fcd_y*gm0; E=2.0e5
    print(f'INPUT R={R} kN  A_wb={A:.1f} mm2  tw={tw} mm  d={d} mm  fy={fy:.1f} MPa (fcd_y={fcd_y})')
    print(f'REPORTED fcc={fcc:.1f} MPa  -> capacity={chk["capacity"]} kN  status={chk["status"]}')
    squash=fcd_y*A/1000; print(f'PHYSICAL_LIMIT squash load A*fy/gm0 = {squash:.1f} kN ; reported/squash = {chk["capacity"]/squash:.1f}x ; fcc/fy = {fcc/fy:.1f}x')
    r=tw/math.sqrt(12); KL=0.7*d; lam=KL/r
    fcd=IS800_2007.cl_7_1_2_1_design_compressisive_stress_plategirder(fy,gm0,lam,E)
    F=fcd*A/1000
    print(f'WEB_STRUT r=tw/sqrt12={r:.3f} mm  KL=0.7d={KL:.1f} mm  KL/r={lam:.1f}  fcd(program fn)={fcd:.2f} MPa  Fcdw={F:.1f} kN  -> {"PASS" if F>=R else "FAIL"} (R={R})')
if __name__=='__main__': main()
