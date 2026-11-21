# Validation Rule Map — Phase W3 Step 2

Source: `src/osdagbridge/core/bridge_types/plate_girder/validator.py` and
`src/osdagbridge/core/utils/osi_validator.py`.
Constant limits: `src/osdagbridge/core/utils/common.py`.

## BridgeInputValidator (per-field validators)

Each method takes `(key: str, inputs: dict)` and returns either
`None` (valid / key not handled) or `(corrected_value, message: str)` (invalid).
All numeric parsing goes through `_to_float` / `_to_int` which return `None`
on non-numeric input.

### validate_basic_inputs

| Key | Limits | Clause source |
|-----|--------|---------------|
| KEY_SPAN = geometry.span | [20.0, 45.0] | Software scope limit |
| KEY_CARRIAGEWAY_WIDTH = geometry.carriageway_width | [4.25, 23.6]; if median==Yes min is 7.5; also >= IRC5 cl_104_3_1_carriageway_width | IRC 5 Cl.104.3.1 |
| KEY_SKEW_ANGLE = geometry.skew_angle | [-15.0, 15.0] | IRC 24 via keyfile |

Missing `geometry.span` returns SPAN_MIN; missing carriageway returns min width; missing skew returns SKEW_ANGLE_MIN.

### validate_material_inputs

Validates girder + deck custom material props ONLY. Cross-bracing / end-diaphragm keys are NOT validated (fall through to return None).

| Key | Limits |
|-----|--------|
| KEY_MATERIAL_GIRDER_DENSITY = material.girder.density | [50.0, 120.0] kN/m3 |
| KEY_MATERIAL_GIRDER_FY = material.girder.fy | [100.0, 1200.0] MPa |
| KEY_MATERIAL_GIRDER_FU = material.girder.fu | [100.0, 1500.0] MPa |
| KEY_MATERIAL_GIRDER_E = material.girder.e | [100.0, 300.0] GPa |
| KEY_MATERIAL_GIRDER_G = material.girder.g | [30.0, 120.0] GPa |
| KEY_MATERIAL_GIRDER_POISSON = material.girder.poisson | [0.0, 0.5] |
| KEY_MATERIAL_GIRDER_THERMAL = material.girder.thermal | [1.0, 30.0] |
| KEY_MATERIAL_DECK_DENSITY = material.deck.density | [18.0, 28.0] kN/m3 |
| KEY_MATERIAL_DECK_FCK = material.deck.fck | [10.0, 80.0] MPa |
| KEY_MATERIAL_DECK_FCTM = material.deck.fctm | [0.5, 6.0] MPa |
| KEY_MATERIAL_DECK_ECM = material.deck.ecm | [15.0, 50.0] GPa |
| KEY_MATERIAL_DECK_THERMAL = material.deck.thermal | [5.0, 15.0] |

NOT validated: all KEY_MATERIAL_CROSS_BRACING_* and KEY_MATERIAL_END_DIAPHRAGM_* keys.

### validate_additional_inputs

| Key | Limits |
|-----|--------|
| KEY_TS_GIRDER_SPACING = typical_section.girder_spacing | [0.5, overall_width/2] |
| KEY_TS_NO_OF_GIRDERS = typical_section.no_of_girders | [2, ceil(2*overall)] int |
| KEY_TS_DECK_OVERHANG = typical_section.deck_overhang | [0.0, overall_width/2] |
| KEY_TS_DECK_THICKNESS = typical_section.deck_thickness | [100, 500] mm |
| KEY_TS_FOOTPATH_WIDTH = typical_section.footpath_width | [min per IRC Cl.104.3.6, carriageway_width] |
| KEY_TS_FOOTPATH_THICKNESS = typical_section.footpath_thickness | [100, 500] mm |
| KEY_CB_WIDTH = typical_section.crash_barrier.width | [0.0, overall/2] |
| KEY_CB_HEIGHT = typical_section.crash_barrier.height | [0.0, 10.0] |
| KEY_CB_LOAD = typical_section.crash_barrier.load | [0.0, 100.0] |
| KEY_CB_POST_SPACING = typical_section.crash_barrier.post_spacing | [0.1, span] |
| KEY_MD_WIDTH = typical_section.median.width | [0.0, overall/2] |
| KEY_MD_HEIGHT = typical_section.median.height | [0.0, 10.0] |
| KEY_MD_LOAD = typical_section.median.load | [0.0, 100.0] |
| KEY_MD_POST_SPACING = typical_section.median.post_spacing | [0.1, span] |
| KEY_RL_HEIGHT = ... | [MIN_RAILING_HEIGHT, 3.0] |

## OsiInputValidator (load-time OSI dictionary validation)

`OsiInputValidator().validate(data) -> OsiValidationResult(is_valid, errors, warnings, corrected_values)`

- Iterates `_BASIC_KEYS = [KEY_SPAN, KEY_CARRIAGEWAY_WIDTH, KEY_SKEW_ANGLE]` — only validates keys that are **present** (missing not blocked).
- Iterates `_ADDITIONAL_KEYS` (46 keys spanning typical-section, crash barrier, median, railing, wearing course, live load, seismic, wind, temperature, deck studs, design options) — only validates **present** keys.
- Validates `design.mode` against `_VALID_DESIGN_MODES = {"Manual", "Optimized", "Standard", "Custom"}`.
- Missing skew normalised to 0.0.
- Delegates each key to `BridgeInputValidator.validate_basic_inputs` / `validate_additional_inputs`.
- A validator exception is caught and recorded as a warning (does not fail load).

## Bridges between core validators and OSI loader

The OSI loader does NOT validate `material.*` keys at load time (they are absent from both `_BASIC_KEYS` and `_ADDITIONAL_KEYS`). See existing issue #96.

## Limits source (`core/utils/common.py`)

- `SPAN_MIN=20.0`, `SPAN_MAX=45.0`
- `CARRIAGEWAY_WIDTH_MIN=4.25`, `CARRIAGEWAY_WIDTH_MAX_LIMIT=23.6`, `CARRIAGEWAY_WIDTH_MIN_WITH_MEDIAN=7.5`
- `SKEW_ANGLE_MIN=-15.0`, `SKEW_ANGLE_MAX=15.0`
- Deck thickness: [100, 500] mm; footpath thickness: [100, 500] mm
- Railing height: [MIN_RAILING_HEIGHT, 3.0] m
