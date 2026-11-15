# Step 0 — Code Study Notes (verified against source, dev branch)

All paths relative to the OsdagBridge clone. Line numbers from the working tree.

## 1. UI → core flow (template_page.py)
- **Design** (`common_design_func`, L627–709): `_prime_material_inputs()` → `validate_required_inputs()` →
  if `is_require_field_changed`: `solve_extend_basic_input_dict(self.input_dict)` (L648) →
  `backend.set_input(self.input_dict)` + `backend.design()` on a worker thread (L689–690).
- **Save .osi** (`saveOSI_inputs`, L793–825): `solve_extend_basic_input_dict(self.input_dict)` (best-effort, L797)
  then `yaml.dump(self.input_dict, f)` (L812). **Flat dict with dotted keys.**
- **Load .osi** (`loadOSI_inputs`, L827–883): `yaml.safe_load` (L839) → `validate_osi_inputs(data)` (L847)
  → reject with error box if invalid → `input_dock.populate_from_dict(data)` (L859) →
  `solve_extend_basic_input_dict` at L867 (best-effort).

**Implication for run_headless.py**: the pipeline for a saved dict is
`yaml.safe_load → validate_osi_inputs → solve_extend_basic_input_dict → set_input → design()`. ✔ matches assignment.

## 2. Limits (common.py L325–331, L1470–1471 — verified)
| Quantity | Limit | Source |
|---|---|---|
| Span | 20.0–45.0 m | SPAN_MIN/SPAN_MAX, validator.py L28–35 |
| Carriageway width | 4.25–23.6 m; ≥7.5 m if median 'Yes' (IRC5 cl104.3.1) | L40–55 |
| Skew | −15° to +15° | L61–68 |
| Custom steel density | 50–120 kN/m³ | validator.py L85–89 |
| Custom Fy | 100–1200 MPa | L92–96 |
| Custom Fu | 100–1500 MPa | L99–103 |
| Custom E | 100–300 GPa | L106–110 |
| Custom G | 30–120 GPa | L113–117 |
| Custom Poisson | 0–0.5 | L120–124 |
| Custom steel thermal | 1–30 ×10⁻⁶/°C | L127–131 |
| Custom deck density | 18–28 kN/m³ | L134–138 |
| Deck fck | 10–80 MPa | L141–145 |
| Deck fctm | 0.5–6 MPa | L148–152 |
| Deck Ecm | 15–50 GPa | L155–159 |
| Deck thermal | 5–15 ×10⁻⁶/°C | L162–166 |

## 3. Custom material keys (material_properties.py `_member_prefix` L556–576, `get_export_fields` L578+; common.py L67–97)
- Girder: `material.girder.{density,fy,fu,e,g,poisson,thermal}`
- Cross bracing: `material.cross_bracing.*` (same 7 fields)
- End diaphragm: `material.end_diaphragm.*` (same 7 fields)
- Deck: `material.deck.{density,fck,fctm,ecm,thermal}`
- Values are strings in the UI (e.g. "78.0"); grade name stored under the combo key
  (`geometry.girder_material`, etc. — exact combo key = KEY_GIRDER / KEY_CROSS_BRACING / KEY_END_DIAPHRAGM / KEY_DECK_CONCRETE_GRADE_BASIC in common.py).
- Custom option literal is `"Custom"` (input_dock.py L36).

## 4. Suspect areas found during reading (to verify at runtime)
1. **`material.girder.density` is never consumed by design** — `_build_material_props`
   (plategirderbridge.py L1169–1244) looks up density from the SQLite DB and falls back to
   `_DEFAULT_DENSITY = 78500.0 N/m³` (L1177); it does **not** read `KEY_MATERIAL_GIRDER_DENSITY`
   even though E/Fy/Fu/Poisson ARE read from input_dict for custom grades. Only the PDF report
   (chap3.py L280) prints it. ⇒ custom steel density likely silently ignored in analysis.
   NOTE: already reported as issue **#20** — duplicate check will mark it.
2. **`material.deck.density`** similarly only referenced in chap3.py L282; issue **#41** exists.
3. **OSI validator does not validate material keys at load** — osi_validator.py `_BASIC_KEYS`
   (L82–86) and `_ADDITIONAL_KEYS` (L89–111) contain no `material.*` keys. `validate_material_inputs`
   exists but is only reachable from the live UI dialog. Out-of-range custom material values in a
   hand-edited .osi pass load validation (possibly unreported bug).
4. **design() re-validates only 4 keys** — `_validate_inputs` (plategirderbridge.py L599–620) checks
   span>0, girders≥2, spacing>0 only; the 20–45 m span limit is NOT enforced at design time
   (matches existing issue #69).
5. **design() mutates input_dict in place** — `_resolve_optimized_bounds_to_mm` and
   `_convert_girder_dims_mm_to_m` overwrite `self.input_dict` (mm→m), i.e. the saved input
   values are converted/overwritten during design (input-mutation check will quantify).
6. **NaN** — `float("nan")` passes `_to_float`; no isfinite checks seen in validator.py;
   issue #88 already covers NaN acceptance.

## 5. Defaults chain (defaults.py)
- `BASIC_INPUT_DICT` L148–167: structure/location/span/carriageway/skew/design_mode = "Optimized",
  girder material = `steel_properties[12]`, deck = `concrete_properies[5]` (DB-ordered lists).
- `solve_extend_basic_input_dict` L870–938: fills Typical Section, Loading, Support Conditions,
  Design Options sub-tab defaults, seeds girder count via `seed_no_of_girders(overall_width)`,
  solves layout (overall width, spacing, overhang) and calls `_on_no_of_girders_changed` which
  writes per-girder dynamic keys `<base>.G{n}.M1` (thickness keys = "All" in Optimized mode,
  SAIL mm values in Custom).

## 6. .osi round-trip concerns
- Save uses `yaml.dump` (default FlowStyle for the nested `project.location` dict? — verify on the real file),
  Load uses `yaml.safe_load` then `_flatten` (osi_validator L200–214) which recurses into nested dicts,
  so `project.location` nested structure is flattened for validation. Round-trip must compare
  dict → yaml.dump → yaml.safe_load → dict for equality AND same design result.
