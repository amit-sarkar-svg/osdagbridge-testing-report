# Comment draft — #41: Custom deck density never reaches `create_deck_load` (always 25 kN/m³)

**Target:** https://github.com/Nidhikhare12/OsdagBridge/issues/41 (duplicate/extra detail; not a new issue)  
**Audit ref:** P2-004 (T4) — OsdagBridge `dev @ d74f56d`, testing repo `osdagbridge-testing-report`

## Suggested comment (copy/paste)

Extra detail (static audit, read-only on `dev @ d74f56d`): the custom deck density key is wired through UI/validation/reporting, but it does not appear to be consumed in the design/load path.

**Key present in UI, validation, and report**
- Defined: `src/osdagbridge/core/utils/common.py:97` — `KEY_MATERIAL_DECK_DENSITY = "material.deck.density"`.
- Validated: `src/osdagbridge/core/bridge_types/plate_girder/validator.py:134` (handles `KEY_MATERIAL_DECK_DENSITY`).
- Reported: `src/osdagbridge/core/reports/chap3.py:19,282` (reads/renders `KEY_MATERIAL_DECK_DENSITY`).
- Written by UI: deck material dialog/priming exports and stores `material.deck.*` fields into `input_dict` (MaterialPropertiesDialog member prefix `material.deck`; input_dock priming/apply path).

**Design/load consumption**
- A key/constant scan (`notes/ui_key_map.csv`) and targeted grep show no reads of `KEY_MATERIAL_DECK_DENSITY` / `material.deck.density` in `plategirderbridge.py` (including the dead-load / `create_deck_load` path), consistent with the reported behavior that analysis falls back to the default density.

**Duplicate check:** aligns with #41; adding concrete definition/validation/report/UI write locations and the absence of design-path consumption for triage.
