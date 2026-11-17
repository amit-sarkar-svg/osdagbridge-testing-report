# Comment draft for issue #133 — additional non-termination case (SW23)

**Target:** [Nidhikhare12/OsdagBridge#133](https://github.com/Nidhikhare12/OsdagBridge/issues/133)

---

Additional evidence: a third valid input reproduces the `design()` non-termination:

**SW23:** span 35.0 m, carriageway 23.6 m, skew +7.5°, footpath Both Sides, median Yes, Optimized, default materials — all within documented limits. `design()` exceeded the 600 s per-case timeout with no result (`evidence/logs/design_sweep_resume.log`, `dictionaries/SW23/case.log`); `dictionaries/SW23/result.json` status = `timeout`.

Together with the two cases in #133 (span 45/cw 15/median Yes/footpaths), all three non-terminating cases combine a large span (35–45 m) with median Yes and/or footpaths and a wide carriageway. Typical valid cases complete in 20–450 s. Please consider bounding the moving-load/envelope solver so these inputs terminate with a clear diagnostic instead of hanging.
