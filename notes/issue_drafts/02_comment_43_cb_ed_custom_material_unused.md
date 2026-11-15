# Comment draft — #43: Cross-bracing and end-diaphragm custom grades stored but unused in design

**Target:** https://github.com/Nidhikhare12/OsdagBridge/issues/43 (duplicate/extra detail; not a new issue)  
**Audit ref:** P2-002 (T4) — OsdagBridge `dev @ d74f56d`, testing repo `osdagbridge-testing-report`

## Suggested comment (copy/paste)

Extra detail (static audit, read-only on `dev @ d74f56d`): the UI/priming path **does** write member-prefixed custom material subkeys for cross-bracing and end-diaphragm into `input_dict`, but these sub-properties are not consumed by the design pipeline — only the grade-name keys appear to be read.

**Keys written (per member) but not design-consumed**
- `material.cross_bracing.{density, fy, fu, e, g, poisson, thermal}`
- `material.end_diaphragm.{density, fy, fu, e, g, poisson, thermal}`

(Grade keys `material.cross_bracing` / `material.end_diaphragm` are read; the sub-properties above are the unused ones.)

**Write path (UI)**
- `src/osdagbridge/desktop/ui/dialogs/material_properties.py:556-576` — `_member_prefix()` maps the member to `material.cross_bracing` / `material.end_diaphragm`.
- `src/osdagbridge/desktop/ui/dialogs/material_properties.py:578-594` — `get_export_fields()` remaps steel template keys (girder-based) to the selected member prefix and returns them for writing.
- `src/osdagbridge/desktop/ui/docks/input_dock.py:324-345, 763-779, 808` — priming/custom selection applies exported fields (and stored custom fields) into the shared `input_dict`.

**Core consumption check**
- A key/constant scan (`notes/ui_key_map.csv`) finds these `material.cross_bracing.*` / `material.end_diaphragm.*` subkeys referenced in core only at `src/osdagbridge/core/utils/common.py` (definitions), with no reads found in `plategirderbridge.py`, `designer.py`, or `analyser.py`. So custom sub-properties entered for cross-bracing/end-diaphragm do not reach the design/material build the way girder subkeys are intended to.

**Duplicate check:** aligns with #43; adding concrete key list + file:line write/read evidence for triage.
