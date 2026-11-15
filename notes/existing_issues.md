# Existing OsdagBridge Issues (open + closed, PRs excluded)

Total: 39

| # | State | Title | Labels |
|---|-------|-------|--------|
| #18 | closed | permission check  ignore |  |
| #19 | open | [Bug] OSI load does not restore _material_custom_fields; Design re-primes custom grades from defaults |  |
| #20 | open | [Bug] Custom steel density from UI/input_dict is ignored in _build_material_props |  |
| #25 | open | Declared font "Ubuntu Sans" is neither bundled nor given a fallback, so the UI never renders in it on macOS |  |
| #41 | open | [Bug] Custom deck density never reaches create_deck_load (always 25 kN/m³) |  |
| #42 | open | [Bug] Default steel grade E 350A cannot complete design — Gs not set |  |
| #43 | open | [Bug] Cross-bracing and end-diaphragm custom grades are stored but unused in design |  |
| #44 | open | [Bug] design() completes and builds CAD when util.fatigue exceeds 100% |  |
| #45 | open | [Bug] Missing DCR categories are written as 0.0 on the output dock |  |
| #48 | open | [Bug] Generated report contains placeholder sections and missing visualizations |  |
| #53 | open | Graphics, Database, and Help menu dropdowns open but options are unresponsive |  |
| #56 | open | Location Bug |  |
| #61 | open | Fx plot titled "Shear Force Diagram" and Tx plot titled "Bending Moment Diagram" in Output Dock |  |
| #64 | open | [Bug] Default RCC railing load is 1.4715 kN/m in the input dictionary but 6.806 kN/m in the design and report |  |
| #65 | open | [Bug] Executive Summary says "design pass" for every component even when Overall Design Status is Fail |  |
| #66 | open | [Bug] Report "Girder Section Dimensions" table prints metres labelled as mm (1.67 mm instead of 1670 mm) |  |
| #67 | open | [Bug] An .osi file with an empty Span passes validation, then solve_extend_basic_input_dict raises ValueError |  |
| #68 | open | [Bug] Report shows blank or N/A for No. of Traffic Lanes, Braking Load, wind and seismic load values |  |
| #69 | open | [Bug] design() accepts out-of-range Span (19.9 m, 45.1 m) and completes without an error |  |
| #70 | open | [Bug] Executive Summary: Girder Spacing and Deck Thickness have no units, and the "<=" symbol is dropped from the status text |  |
| #71 | open | [Bug] Save Input overwrites committed deck and wearing-course thicknesses with defaults |  |
| #72 | open | [Bug] End Diaphragm tab displays cross-bracing results instead of its own output dictionary |  |
| #73 | open | [Bug] Girder support-reaction fields disagree with the reaction labels in the same plot |  |
| #74 | open | [Bug] Runtime deck layout uses a fixed 0.5 m crash-barrier width instead of the input's 0.45 m |  |
| #76 | open | [Bug] Custom material dialog restricts inputs to 1 decimal place (e.g. Poisson's ratio 0.31 cannot be entered) |  |
| #81 | open | [Bug] PDF includes Material Take-off and References even when unchecked |  |
| #82 | open | [Bug] Incorrect MPa unit labels for steel elastic and shear modulus in exported Excel results |  |
| #84 | open | [Bug] Crash barrier area is mm² in the defaults but m² in the Additional Inputs dialog, so the Material Take-off shows 0.00 MT for the crash barrier |  |
| #85 | open | [Bug] 3D CAD model not displayed after unlock and redesign (second run in the same session) |  |
| #86 | open | [Bug] Selected wind speed, exposed height and terrain are replaced by defaults before analysis |  |
| #87 | open | [Bug] Seismic load generation runs before governing vehicle selection and uses zero live-load mass |  |
| #88 | open | [Bug] OSI validation accepts NaN physical inputs before layout and model construction |  |
| #89 | open | [Bug] Skewed four-girder bridges retain only one per-girder design result |  |
| #90 | open | [Bug] Optimized custom section choices are ignored and continuous bounds fail as unresolved dictionaries |  |
| #91 | open | [Bug] Zero-overhang models omit the two outer physical girders from self-weight loading |  |
| #92 | open | [Bug] Canonical temperature inputs do not create thermal load cases in the normal design pipeline |  |
| #93 | open | [Bug] CAD uses fixed 3 m cross-bracing spacing despite 13 m in the design output |  |
| #94 | open | [Bug] Girder Design Check summary reports 8 checks but displays only 6 check cards |  |
| #95 | open | clarification required-Stress Limitation displays 0.9 × Fy instead of the stated Fy / γM0 |  |
