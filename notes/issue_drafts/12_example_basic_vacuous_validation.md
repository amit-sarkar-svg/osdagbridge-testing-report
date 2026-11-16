# [Docs/Examples] `example_basic.yaml` uses placeholder keys but passes `validate_osi_inputs` vacuously

**Filed:** [Nidhikhare12/OsdagBridge#128](https://github.com/Nidhikhare12/OsdagBridge/issues/128) — open (filed 2026-11-17)

**Environment**
- OsdagBridge `dev` @ `d74f56d` (2026-07-26)
- macOS (Intel), conda env `osdagbridge-env`, Python 3.12.16
- Finding type: **T7 (oddity/misleading example; validator behavior may be intentional)**

**Description**
`examples/plate_girder/example_basic.yaml` contains a placeholder schema (e.g. `project.span_m`) rather than the real dotted OSI input keys used by the application (e.g. `geometry.span`, `geometry.carriageway_width`, `geometry.skew_angle`). Despite not providing those real inputs, it passes `validate_osi_inputs` with no errors/warnings because the validator only polices values for *present* known keys and does not require basic inputs to be present at load.

**Steps to reproduce**
1. Open/parse `examples/plate_girder/example_basic.yaml` from the source tree (`dev @ d74f56d`).
2. Run OSI validation on the loaded data (`validate_osi_inputs`).

**Observed behavior (evidence)**
- Top-level key: `['project']` (no real dotted input keys such as `geometry.span` / `geometry.carriageway_width` / `geometry.skew_angle`)
- `validate_osi_inputs` result: `is_valid=True`, `errors=[]`, `warnings=[]`

(Recorded in `evidence/logs/phase1_examples.txt`; `tests/test_phase1_packaging.py::test_examples_parse_and_validate` confirms current state.)

**Expected behavior**
An illustrative/basic example would typically use the actual OSI key schema so users can load/adapt it meaningfully. Alternatively, if placeholder examples are intentional, they should be clearly labeled as non-loadable templates and/or validation/documentation should make their status explicit.

**Actual behavior**
The shipped example uses a non-real placeholder schema yet is accepted by the OSI loader/validator vacuously, which can be misleading.

**Impact**
- Users may assume `example_basic.yaml` is a valid, usable input example when it does not specify the required/real input keys.
- Can cause confusion when adapting the example for actual design runs.

**Suggested fix**
- Replace/update `example_basic.yaml` to use real dotted OSI keys and representative valid values, **or**
- Clearly mark it as a conceptual placeholder (not a loadable input) and/or adjust documentation/validation messaging so its non-runnable nature is explicit.

**Duplicate check**
Searched existing OsdagBridge issues (open+closed, full titles/bodies, refreshed `notes/issues_raw.json` through #126) for `example_basic` / placeholder-key example terms — no matching issue found. (Related load/validation issues like #19/#67/#69/#88/#96 concern different behaviors.)

**Notes**
This is reported as **T7** because the validator’s tolerant “validate only present known keys” behavior may be intentional; the shipped example content is nonetheless potentially misleading.
