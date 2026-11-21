# Safety-relevant calculation functions (Phase 5, session 4)

| # | Function | File:line | Cited clause/source | Signature |
|---|----------|-----------|---------------------|-----------|
| 1 | cl_603_3_3_2_plastic_shear_resistance | irc22_2015.py:669 | IRC22 603.3.3.2(1) + IS800 8.4.1; Vn=Av·fyw/√3, Vd=Vn/γm0, γm0=1.10 | (section_type,fyw,fabrication,h,d,tw,bf,tf) |
| 2 | cl_604_3_2_deflection_limits | irc22_2015.py:1063 | IRC22 604.3.2; live≤L/800, total≤L/600, cant total≤Lc/300, cant live≤Lc/400 | (span_m,defl_live_impact_mm,defl_total_mm,cantilever_m,...) |
| 3 | cl_603_2_1_effective_width_simply_supported | irc22_2015.py:227 | IRC22 603.2.1; inner beff=min(Lo/4,B), outer=min(Lo/8,B1/2)+min(B0,Lo/8) | (Lo,beam_type,B,B1,B2,B0) |
| 4 | cl_604_3_modular_ratio | irc22_2015.py:913 | IRC22 604.3; m_short=Es/Ecm≥7.5, m_long=Es/(Kc·Ecm)≥15 | (fck,concrete_grade,Ecm,Eci,Kc,aggregate_type) |
| 5 | _moment_capacity_kNm | deckdesign.py:71 | IRC112/IS456 stress block; xu=0.87fyAs/(0.36fck b), Mu=0.87fyAs(d−0.42xu) | (fy,As,d,fck,b) |
| 6 | _required_steel_mm2 | deckdesign.py:84 | exact inverse of #5 (quadratic) | (M_ULS,fy,d,fck,b) |
| 7 | _min_steel_mm2 | deckdesign.py:102 | IRC112 Cl.16.5.1; 0.26(fctm/fy)·b·d, min 0.0013·b·d | (fctm,fy,d,b) |
| 8 | _v_Rd_c_MPa | deckdesign.py:159 | IRC112:2020 Eq.10.1; v_Rd,c=max(0.12k(80ρfck)^0.33, 0.031k^1.5√fck) | (As,d,fck,b) |
| 9 | cl_603_3_3_2_shear_buckling_post_critical | irc22_2015.py:754 | IRC22 603.3.3.2(2)(a)/IS800 8.4.2.2(a); τcr=Kvπ²E/(12(1-μ²))(tw/d)² | (Av,c,d,tw,fyw,stiffeners_at_support_only,mu) |
| 10 | cl_8_4_2_2_K_v_Simple_postcritical | is800_2007.py:1349 | IS800 8.4.2.2(a); Kv table (support only=5.35) | (support,c,d) |

Notes: all call signatures verified by reading source. Clauses above are quoted from the code's own docstrings/comments (not from memory). Where a function cites a clause but not an explicit formula, expected values are derived from the formula in its own docstring. Items whose source cannot be verified are marked T7 in the results.
