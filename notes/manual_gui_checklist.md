# Manual GUI checklist (X2, partial; reproduce by hand)
1. Press Design twice in a row on span 30, carriageway 15, skew 0, Optimized: confirm no crash (my headless probe says UI path is OK). Then lock/unlock and redesign.
2. Type "nan" in span, skew, carriageway fields: check whether the dock accepts it (QDoubleValidator may block; headless validator accepts NaN).
3. Median = No with empty carriageway width: which minimum is shown (4.25 vs 7.5)?
4. Project location dialog: enter latitude 999 / longitude nan; observe crash or weather lookup.
5. Material dialog: Custom... twice; are earlier custom values restored? Poisson 0.25 shown as 0.2/0.3?
6. Press Design twice quickly: duplicate run or stuck state.
7. Clear a required field then Design: popup shown? Widget blank vs dict default.
Screenshots: each dialog state and the error popup.
