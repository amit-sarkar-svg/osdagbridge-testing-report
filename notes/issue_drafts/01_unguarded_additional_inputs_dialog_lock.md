# [Bug] Toggling input lock can crash when Additional Inputs dialog was never opened (`_additional_inputs_dialog` is None)

**Filed:** [Nidhikhare12/OsdagBridge#97](https://github.com/Nidhikhare12/OsdagBridge/issues/97) — open (filed 2026-11-15)

**Environment**
- OsdagBridge `dev` @ `d74f56d` (2026-07-26)
- macOS (Intel), conda env `osdagbridge-env`, Python 3.12.16
- Finding type: **T3 (static, code-read; not executed as a runtime repro in this session)**

**Description**
Lock/unlock propagates state to the Additional Inputs dialog, but `InputDock.toggle_lock()` dereferences the dialog without checking whether it has been instantiated. `template_page` creates the dialog lazily, so toggling the input lock before ever opening Additional Inputs can raise `AttributeError` on `None`.

**Steps to reproduce (expected from code path)**
1. Launch OsdagBridge and open the plate girder module (do **not** open “Additional Inputs/Geometry”).
2. Trigger the input lock/unlock toggle (padlock / “Clear Results” → Continue path that flips lock state).

**Expected behavior**
Lock state changes safely regardless of whether the Additional Inputs dialog has been created.

**Actual behavior (from static analysis)**
`InputDock.toggle_lock()` calls `lock()` on `self.parent._additional_inputs_dialog` unconditionally; if the dialog was never created, this is `None`.

**Evidence (file:line, read-only)**
`src/osdagbridge/desktop/ui/docks/input_dock.py:856-859`:
```python
self.is_locked = not self.is_locked

# Update Additional Input State (Lock/Unlock)
self.parent._additional_inputs_dialog.lock(lock=self.is_locked)
```

`src/osdagbridge/desktop/ui/template_page.py:124` initializes lazily:
```python
self._additional_inputs_dialog: AdditionalInputs | None = None
```
Created on demand in `_get_additional_inputs()` (`template_page.py:440-447`), while other call sites guard with `if self._additional_inputs_dialog is not None:` (e.g. `:454,615,862`).

**Suggested fix (diff sketch)**
```diff
--- a/src/osdagbridge/desktop/ui/docks/input_dock.py
+++ b/src/osdagbridge/desktop/ui/docks/input_dock.py
@@
         self.is_locked = not self.is_locked

         # Update Additional Input State (Lock/Unlock)
-        self.parent._additional_inputs_dialog.lock(lock=self.is_locked)
+        dlg = getattr(self.parent, "_additional_inputs_dialog", None)
+        if dlg is not None:
+            dlg.lock(lock=self.is_locked)
```

**Duplicate check**
Searched existing issues (open+closed, full titles/bodies in `notes/issues_raw.json`) for `_additional_inputs_dialog` / related AttributeError-on-lock terms — no matching issue found. (Not #96.)

**Notes**
Static finding (code-read); a quick GUI confirm (toggle lock before opening Additional Inputs) would strengthen it.
