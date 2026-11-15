# Comment draft — #19: OSI load does not restore `_material_custom_fields`; Design re-primes custom grades from defaults

**Target:** https://github.com/Nidhikhare12/OsdagBridge/issues/19 (duplicate/extra detail; not a new issue)  
**Audit ref:** P2-005 (T4) — OsdagBridge `dev @ d74f56d`, testing repo `osdagbridge-testing-report`

**Status:** Comment draft prepared (2026-11-15). Upstream posting on target issue: pending confirmation.

## Suggested comment (copy/paste)

Extra detail (static audit, read-only on `dev @ d74f56d`) pinpointing where the custom-material state is lost on load/populate:

**`populate_from_dict` restores widgets/dict but not custom-field state**  
`src/osdagbridge/desktop/ui/docks/input_dock.py:1048-1083` (`populate_from_dict`):
- Replaces `parent.input_dict` in-place with loaded `data`.
- Walks widgets by `objectName` and sets `QLineEdit`/`QComboBox` values (adds a missing combo item if needed, sets selection silently), with signals blocked.
- Marks `is_require_field_changed = True` and emits `input_value_changed`.

It does **not** restore `self._material_custom_fields` (base/custom property fields stored per custom material name) or the related prior-selection tracking used by the material flow.

**Why this matters**
- `_prime_material_inputs()` (`input_dock.py:324-345`) and custom material handling (`:763-779, :808`, etc.) read `self._material_custom_fields` when (re)building/exporting/applying custom material values. Without restoring it on load, a loaded OSI containing custom grade selections/values cannot rehydrate the in-memory custom-field map, so subsequent Design/priming falls back to defaults/DB behavior as described in #19.

**Duplicate check:** aligns with #19; adding the exact `populate_from_dict` behavior and its missing `_material_custom_fields` restoration for triage.
