# Comment draft for #135 (T4 duplicate, adds root cause + proven fix)

Root cause found for the second-`design()` crash.

`PlateGirderBridge.design()` calls `_convert_girder_dims_mm_to_m()` every time (plategirderbridge.py:683, function at :536-589). It divides the values in `self.input_dict` by 1000 **in place**, so a second `design()` on the same object (without a new `set_input()`) divides again.

Reproduction (fresh process, twice; script `scripts/probe_double_convert.py`, input `test_cases/generated/A1_params.json`: span 30, carriageway 15, skew 0, no footpath, no median, Optimized):
- before: `girder depth G1.M1 = 1670` (mm)
- after run 1: `1.67` (m, correct)
- run 2: `ValueError: math domain error` (LTB check); `input_dict` depth is now `0.00167`.

Fix proof (monkeypatch only, no edit of the repo): restoring a pristine deep copy of `input_dict` before each `design()` gives run 1 depth = run 2 depth = 1.67 and no crash (`scripts/probe_double_convert_fix.py`). Suggested fix: convert into a copy, or keep the mm values and write converted values to a separate dict.

Note: the desktop path (`template_page.py:689-690`) calls `set_input(input_dict)` before every `design()`, and `set_input` does not alias the UI dict, so I could not reproduce the crash through that path for this input. The defect is an API-contract problem (retry or redesign on the same object).
