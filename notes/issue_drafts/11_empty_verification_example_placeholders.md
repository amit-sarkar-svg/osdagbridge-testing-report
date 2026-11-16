# [Docs/Examples] `verification_case_01.yaml` and `verification_case_02.yaml` are empty placeholders that fail OSI validation

**Filed:** [Nidhikhare12/OsdagBridge#127](https://github.com/Nidhikhare12/OsdagBridge/issues/127) — open (filed 2026-11-17)

**Environment**
- OsdagBridge `dev` @ `d74f56d` (2026-07-26)
- macOS (Intel), conda env `osdagbridge-env`, Python 3.12.16
- Finding type: **T6 (documentation/example content)**

**Description**
The example files `examples/plate_girder/verification_case_01.yaml` and `examples/plate_girder/verification_case_02.yaml` are empty/comment-only placeholders (parsed as no valid input dictionary). As shipped, they cannot be loaded as meaningful verification cases and fail OSI input validation.

**Steps to reproduce**
1. In the OsdagBridge source tree (`dev @ d74f56d`), open:
   - `examples/plate_girder/verification_case_01.yaml`
   - `examples/plate_girder/verification_case_02.yaml`
2. Parse/validate them as OSI inputs (e.g. `yaml.safe_load` + `validate_osi_inputs` / load path).

**Expected behavior**
Verification example files should contain loadable, meaningful input data (or be clearly marked/excluded) so users/contributors can use them as intended reference/verification cases.

**Actual behavior**
Both files load without a valid input dictionary and are rejected by validation:
- `verification_case_01.yaml`: `top_keys: NoneType`, `validate.is_valid: False`, `validate.errors: ['File does not contain a valid input dictionary.']`
- `verification_case_02.yaml`: `top_keys: NoneType`, `validate.is_valid: False`, `validate.errors: ['File does not contain a valid input dictionary.']`

(Recorded in `evidence/logs/phase1_examples.txt`; `tests/test_phase1_packaging.py::test_examples_parse_and_validate` confirms current state.)

**Impact**
- Users expecting runnable verification examples cannot use these files.
- Misleading repository examples/documentation signal for plate-girder verification cases.

**Suggested fix**
- Populate `verification_case_01.yaml` and `verification_case_02.yaml` with valid, representative `.osi`/YAML inputs that pass `validate_osi_inputs`, **or**
- Clearly label them as placeholders/TODO (and/or move them out of user-facing examples) until real verification cases are provided.

**Duplicate check**
Searched existing OsdagBridge issues (open+closed, full titles/bodies, refreshed `notes/issues_raw.json` through #126) for `verification_case` / empty example placeholder terms — no matching issue found. (Not #96.)

**Notes**
`examples/plate_girder/example_basic.yaml` is a separate case (uses placeholder/non-real keys but passes `validate_osi_inputs` vacuously) tracked as P1-006 (T7).
