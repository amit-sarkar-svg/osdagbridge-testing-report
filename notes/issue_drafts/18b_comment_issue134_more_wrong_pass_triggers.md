# Comment draft for issue #134 — additional reproduction (broader trigger)

**Target:** [Nidhikhare12/OsdagBridge#134](https://github.com/Nidhikhare12/OsdagBridge/issues/134)

---

Additional evidence: the wrong-PASS condition is **not limited** to cw 7.5 + median + both footpaths. A second, very different valid input reproduces the same silent live-load skip → zero ULS demand → PASS:

**Second repro (SW15):** span 45.0 m, carriageway 23.6 m, skew −7.5°, footpath None, median No, design mode Optimized, default materials — all within documented limits.

Observed (executed, `dictionaries/SW15/case.log`, `dictionaries/SW15/output.json`):
- `analyser.py:1998 UserWarning: Envelope-based governing LL detection failed ("not all values found in index 'Element'..."); skipping LL creation.`
- `steeldesign.details.moment.mu_applied = 0.0`, ULS Flexure DCR 0.000, all `util.* = 0.0`
- `Status : PASS`, `Maximum DCR 0.4545` (only stiffener/other excluded checks nonzero)

This shares the exact root cause with #134 (`env_lc.sel(Element=gov_element)` KeyError at `analyser.py:1991`, swallowed at :1998 → `ll_load_case = None`). A **third** valid input also reproduces it:

**Third repro (SW22):** span 25.0 m, carriageway 23.6 m, skew 0°, footpath Both Sides, median No → same `Element` index error, `mu_applied = 0.0`, verdict PASS (max DCR 0.2767).

The three confirmed affected inputs have different spans (25/30/45), widths (7.5/23.6), skews (0/−7.5), and median/footpath settings — so the trigger is in the governing-LL envelope element lookup itself, not in a specific geometry setting. Other swept cases with similarly high girder counts (SW07/SW09/SW13/SW14/SW21, girders 10–11) complete with normal nonzero demands, so it is not simply girder count.

Suggest broadening the issue title/scope to "governing-LL detection failure causes silent zero-live-load design with PASS verdict", and add a regression covering both inputs.
