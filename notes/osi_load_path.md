# OSI Save/Load Path Analysis — Phase W4 STEP 2

## saveOSI_inputs (template_page.py:793-826)
- Calls solve_extend_basic_input_dict(self.input_dict) (line 797) to populate defaults, catching any exception silently (line 798).
- Opens QFileDialog.getSaveFileName with filter "Input Files(*.osi)" (line 802-806).
- Writes with yaml.dump(self.input_dict, input_file) (line 812) — UNSAFE dumper, can emit !!python/object, !!set, !!python/tuple tags.
- Shows "Saved OSI Successfully!" unconditionally on success (line 817); shows error only on exception (line 821-824).
- No extension enforcement: does not check/append .osi; relies on dialog filter.
- No overwrite confirmation: overwrites existing file silently.

## loadOSI_inputs (template_page.py:827-883)
- Opens QFileDialog.getOpenFileName with filter "Input Files (*.osi)" (line 828-833).
- yaml.safe_load(f) (line 839) — safe loader, rejects !!python/object, !!set, etc.
- validate_osi_inputs(data) called BEFORE populate_from_dict (line 847-857). If invalid, shows error dialog and returns — UI is NOT populated (no half-updated state).
- self.input_dock.populate_from_dict(data) (line 859) — populates UI.
- self._additional_inputs_dialog.set_input_dictionary(...) if dialog exists (line 862-863).
- solve_extend_basic_input_dict(self.input_dict) called at line 867, wrapped in try/except pass (line 869-870) — errors silently swallowed.
- cad_comp_widget.update_from_osdag_inputs (line 868), also try/except pass.
- Exceptions caught broadly at line 878: "Could not load OSI file".

## Key findings (static, read-only)
1. yaml.dump vs yaml.safe_load mismatch: save uses unsafe dumper, load uses safe loader. Values containing numpy scalars/tuples/sets may be dumped with unsafe tags and fail to load back. (Tracked as P4I-001/T2.)
2. No file extension enforcement: code does not check/enforce .osi extension; relies on dialog filter only. A file named foo.txt, foo.yaml, foo.OSI can be saved/loaded.
3. No overwrite confirmation: saveOSI_inputs overwrites existing files silently.
4. solve_extend_basic_input_dict exceptions silently swallowed (line 869-870): if the loader's post-load solve fails, the UI has already been populated (populate_from_dict ran at line 859), so the UI shows data that the solver rejected.
5. No material key validation at load: _ADDITIONAL_KEYS/_BASIC_KEYS do not include material.* keys (#96).

## Evidence (read-only, file:line)
- src/osdagbridge/desktop/ui/template_page.py:793-883 — saveOSI_inputs and loadOSI_inputs
- src/osdagbridge/core/utils/osi_validator.py:82-160 — OsiInputValidator
