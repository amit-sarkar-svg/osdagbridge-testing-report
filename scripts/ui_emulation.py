#!/usr/bin/env python
"""Headless emulation of the UI's material priming step.

Why: the app always runs InputDock._prime_material_inputs() before Design
(template_page.py L636). It populates the member-prefixed material property
keys (material.girder.fy, ...) from the MaterialPropertiesDialog for the
selected grade, using _update_input_dict semantics (empty value -> None).

This module reproduces that logic WITHOUT Qt by reusing the dialog's pure
methods via MaterialPropertiesDialog.__new__ (widget side effects skipped),
so the headless pipeline sees exactly the input_dict the GUI would have at
Design time. Logic copied from:
  - material_properties.py __init__ L172-217 (attribute setup)
  - material_properties.py _load_material_info_for_view L707-758 (pure part)
  - material_properties.py get_export_fields L578+ / _member_prefix L556-576
  - input_dock.py _update_input_dict L1029-1046
"""
from __future__ import annotations

import re

MATERIAL_COMBO_KEYS = [
    "material.girder",       # KEY_GIRDER
    "material.cross_bracing",  # KEY_CROSS_BRACING
    "material.end_diaphragm",  # KEY_END_DIAPHRAGM
    "material.deck",           # KEY_DECK_CONCRETE_GRADE_BASIC
]
MATERIAL_CUSTOM_OPTION = "Custom"

from osdagbridge.desktop.ui.dialogs.material_properties import MaterialPropertiesDialog

from osdagbridge.core.utils.common import (
    KEY_MATERIAL_GIRDER_DENSITY, KEY_MATERIAL_GIRDER_FY, KEY_MATERIAL_GIRDER_FU,
    KEY_MATERIAL_GIRDER_E, KEY_MATERIAL_GIRDER_G, KEY_MATERIAL_GIRDER_POISSON,
    KEY_MATERIAL_GIRDER_THERMAL,
    KEY_MATERIAL_DECK_DENSITY, KEY_MATERIAL_DECK_FCK, KEY_MATERIAL_DECK_FCTM,
    KEY_MATERIAL_DECK_ECM, KEY_MATERIAL_DECK_THERMAL,
    KEY_GIRDER, KEY_CROSS_BRACING, KEY_END_DIAPHRAGM, KEY_DECK_CONCRETE_GRADE_BASIC,
)

# Basic keys known to BASIC_INPUT_DICT (input_dock._update_input_dict fallback)
from osdagbridge.core.bridge_types.plate_girder.defaults import BASIC_INPUT_DICT


def _member_prefix(member_key: str) -> str:
    if member_key == KEY_DECK_CONCRETE_GRADE_BASIC:
        return "material.deck"
    if member_key == KEY_CROSS_BRACING:
        return "material.cross_bracing"
    if member_key == KEY_END_DIAPHRAGM:
        return "material.end_diaphragm"
    return "material.girder"


def _dialog_fields_for(grade: str, member_key: str, custom_fields: dict | None = None) -> dict:
    """Replicates MaterialPropertiesDialog(read_only=True, selected_material=grade,
    member=member_key, custom_fields=custom_fields) -> form_data['fields'] (pure part)."""
    dlg = MaterialPropertiesDialog.__new__(MaterialPropertiesDialog)  # skip QDialog.__init__
    dlg.validator = None
    dlg.read_only = True
    dlg.selected_material = grade
    dlg.member = member_key
    dlg.custom_fields = custom_fields
    dlg.is_deck_material = (member_key == "Deck") or dlg._is_deck_material(grade)
    # widget-only attributes used by _populate_fields(); kept empty = no-op
    dlg.field_inputs = {}
    try:
        dlg.material_input = None
    except Exception:
        pass
    # _load_material_info_for_view calls self.material_input.setText + _populate_fields;
    # guard against the widget call by temporarily patching setText behaviour
    class _NoWidget:
        def setText(self, *_):
            pass
    dlg.material_input = _NoWidget()
    dlg.form_data = {"material": grade, "fields": {}}  # created in real __init__ L214-217
    dlg._load_material_info_for_view(grade)
    return dict(dlg.form_data["fields"])


def _update_input_dict(d: dict, key: str, value):
    """input_dock.py _update_input_dict: empty/None -> BASIC_INPUT_DICT.get(key)."""
    if value is None or value == "":
        d[key] = BASIC_INPUT_DICT.get(key)
    else:
        d[key] = value


def prime_material_inputs(d: dict, mode: str = "osi_load") -> None:
    """Emulate InputDock._prime_material_inputs (input_dock.py L324-342).

    mode='osi_load'   : custom_fields=None — exactly what happens after loading
                        a .osi, because _material_custom_fields is not restored
                        (issue #19). Custom-grade property values get wiped.
    mode='in_session' : emulates the stored _material_custom_fields by feeding
                        the dict's own property values back as custom_fields —
                        what happens when the user created the custom material
                        in this GUI session and clicks Design without reload.
    """
    for member_key in MATERIAL_COMBO_KEYS:
        selected = str(d.get(member_key) or "").strip()
        if not selected or selected == MATERIAL_CUSTOM_OPTION:
            continue
        fields = _dialog_fields_for(selected, member_key, custom_fields=None)
        prefix = _member_prefix(member_key)
        if mode == "in_session":
            if member_key == KEY_DECK_CONCRETE_GRADE_BASIC:
                custom_grade = _is_unknown_concrete(selected)
            else:
                custom_grade = (
                    fields.get(KEY_MATERIAL_GIRDER_FY) in ("", None)
                    and fields.get(KEY_MATERIAL_GIRDER_FU) in ("", None)
                )
            if custom_grade:
                stored = {
                    k.replace(prefix, "material.girder"): v
                    for k, v in d.items()
                    if k.startswith(prefix + ".") and v not in (None, "")
                }
                if stored:
                    fields = _dialog_fields_for(selected, member_key, custom_fields=stored)
        for k, v in fields.items():
            fk = k.replace("material.girder", prefix) if k.startswith("material.girder") else k
            _update_input_dict(d, fk, v)
        _update_input_dict(d, member_key, selected)


def _is_unknown_concrete(grade: str) -> bool:
    dlg = MaterialPropertiesDialog.__new__(MaterialPropertiesDialog)
    return dlg._get_concrete_from_code(grade) is None
