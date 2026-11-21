# [Typo/Naming] UI schema key misspelled as `section.additonal_geometry` (missing "i")

**Environment**
- OsdagBridge `dev` @ `d74f56d` (2026-07-26)
- Finding type: **T6 (typo/naming in internal UI schema key)**

**Description**
An internal UI section key constant is defined and used with a misspelling: `section.additonal_geometry` (missing the "i" in "additional"). While this appears to be an internal title/section identifier (not a persisted user data key in `BASIC_INPUT_DICT`), inconsistent naming can cause confusion and makes future lookups/refactors error-prone.

**Evidence (read-only, file:line)**
- `src/osdagbridge/core/utils/common.py:298` defines:
  ```py
  KEY_SECTION_ADDITIONAL_GEOMETRY = "section.additonal_geometry"
  ```
- `src/osdagbridge/core/bridge_types/plate_girder/ui_fields.py:180` uses:
  ```py
  (KEY_SECTION_ADDITIONAL_GEOMETRY, None, TYPE_TITLE, None, True, "No Validator",
  ```
- Phase 2 UI schema capture (`evidence/logs/phase2_main_inputs.txt:26`) records:
  `ROW|section.additonal_geometry|title|label=None|vals=None|default=None|required=None|disabled=None|member=None|action=None`

**Expected behavior**
Internal keys/names should be consistently spelled (e.g. `section.additional_geometry`) to avoid confusion and maintenance mistakes.

**Actual behavior**
The key string is misspelled as `section.additonal_geometry`.

**Impact**
- Low runtime impact if treated purely as an internal identifier, but increases risk of mismatched references in future UI/schema changes and reduces code clarity/searchability.

**Suggested fix**
- Rename the key value (and constant name if desired for consistency) to `section.additional_geometry` and update all references/usages accordingly.
- Verify no external persisted data depends on the misspelled identifier before renaming (if any serialized schema uses it, consider a compatibility alias/migration).

**Duplicate check**
Searched refreshed existing OsdagBridge issues (open+closed, `notes/issues_raw.json` through #126) for `additonal_geometry` / `additional_geometry` typo terms — no matching issue found. (Not #96.)
