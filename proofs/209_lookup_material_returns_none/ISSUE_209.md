# [Bug/Robustness] `PlateGirderBridge._lookup_material` returns `None` for an unknown grade or property and raises `IndexError` for an empty name

**Environment:** macOS 13.6 (Darwin 22.6.0), Python (conda env `osdagbridge-env`), OsdagBridge branch `dev`, commit `d74f56d`.

## Description
`_lookup_material(material_name, property)` (`plategirderbridge.py:1124-1167`) is annotated `-> float`. Its docstring says it "falls back to the default value if the DB is missing or the material is not found". When the query returns no row, the function falls off the end and returns `None`, with no fallback and no error. The callers at `plategirderbridge.py:1181-1201` (E, ν, ρ, fy, fu) use the result directly, so a wrong grade string surfaces later as an unrelated `TypeError`.

Related problems:
- `material_name[0]` raises `IndexError` for `""` (line 1136).
- The `except sqlite3.Error` message interpolates the class `sqlite3.Error`, not the caught exception, so the real database error is lost (line 1167).
- If `execute` raises, `con.close()` is skipped.

## Steps to reproduce
```python
from osdagbridge.core.bridge_types.plate_girder.plategirderbridge import PlateGirderBridge
b = PlateGirderBridge()
b._lookup_material("E 999", "Yield Strength")   # -> None
b._lookup_material("", "Yield Strength")        # -> IndexError: string index out of range
```
Script: `scripts/probe_cands3.py`. Output was identical in two fresh processes (`evidence/logs/probe_cands3*.log`).

## Expected
The function either returns a float, as its type annotation and docstring state, or raises a clear `LookupError` naming the grade and property.

## Actual
It returns `None` silently, and an empty name gives an `IndexError`.

## Suggested fix
```diff
-        if material_name.startswith('Fe'):
+        if not material_name:
+            raise LookupError("Empty material name in PlateGirderBridge._lookup_material")
+        if material_name.startswith('Fe'):
 ...
-        try:
-            con = sqlite3.connect(_DB_PATH)
+        try:
+            with closing(sqlite3.connect(_DB_PATH)) as con:
 ...
-        except sqlite3.Error:
-            raise LookupError(f"Error querying material database ...: {sqlite3.Error}")
+        except sqlite3.Error as exc:
+            raise LookupError(f"Error querying material database for {material_name!r}/{property!r}: {exc}") from exc
+        raise LookupError(f"Material {material_name!r} has no {property!r} in {table}")
```

## Severity note
Grades normally come from a dropdown, so this is a robustness and API-contract defect (low severity). It matters for .osi files edited by hand or carrying a stale grade name.

## Duplicate check
I searched titles and bodies for `_lookup_material`, "material database" and sqlite. The hits were #187, #117, #42, #20, #169 and #98. #169 covers a wrong table name in cross-bracing, and #98 covers packaging metadata. None reports the missing-row `None` return.
