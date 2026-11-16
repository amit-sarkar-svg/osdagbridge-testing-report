# [Bug/I-O] `saveOSI_inputs` uses `yaml.dump` (unsafe tags) while load uses `yaml.safe_load` — round-trip can fail

**Filed:** [Nidhikhare12/OsdagBridge#131](https://github.com/Nidhikhare12/OsdagBridge/issues/131) — open (filed 2026-11-17)

**Environment**
- OsdagBridge `dev` @ `d74f56d` (2026-07-26)
- macOS (Intel), conda env `osdagbridge-env`, Python 3.12.16
- Finding type: **T2 (likely save/load round-trip bug)**

**Description**
`TemplatePage.saveOSI_inputs` writes the input dictionary with `yaml.dump(...)` (default/unsafe dumper), while `loadOSI_inputs` reads with `yaml.safe_load(...)`. For certain Python/object types that can appear in state (e.g. numpy scalars, tuples, sets), `yaml.dump` emits Python-specific tags (`!!python/...`, `!!set`, `!!python/tuple`) that `yaml.safe_load` refuses to construct, causing a saved OSI file to fail loading.

**Steps / Reproduction (executed, direct YAML behavior)**
```python
import yaml, numpy as np
d = {"a": np.float64(1.5), "t": (1, 2), "s": {1, 2}, "f": 1.5}
dumped = yaml.dump(d)
print(dumped)
yaml.safe_load(dumped)  # raises ConstructorError
```

**Observed (executed)**
- Dump includes `!!python/object/apply:numpy._core.multiarray.scalar`, `!!set`, `!!python/tuple`
- `yaml.safe_load(dumped)` raises:
  `ConstructorError: could not determine a constructor for the tag 'tag:yaml.org,2002:python/object/apply:numpy._core.multiarray.scalar'`

(Evidence: `evidence/logs/trackI_yaml_dump_safe_load.txt`)

**Code (read-only, file:line)**
- Save: `src/osdagbridge/desktop/ui/template_page.py` (~793–820) — `yaml.dump(self.input_dict, input_file)` then shows "Saved OSI Successfully!"
- Load: `src/osdagbridge/desktop/ui/template_page.py` (~827–850+) — `data = yaml.safe_load(f)` then validates/populates

**Expected behavior**
OSI save and load should be round-trip compatible: files saved by the app should be loadable by the app without unsafe/Python-specific tags that `safe_load` cannot parse.

**Actual behavior**
Save uses unsafe `yaml.dump` while load enforces `yaml.safe_load`, so dictionaries containing types like numpy scalars/tuples/sets can be written but not read back.

**Impact**
Potential data-loss/UX issue: a user can save successfully but fail to reload the same OSI if such types are present in `self.input_dict`.

**Suggested fix (diff idea)**
Serialize with a safe, JSON-like representation (or normalize types before dumping) and/or use `yaml.safe_dump` with explicit representers for supported types:
```diff
-            with open(filePath, 'w') as input_file:
-                yaml.dump(self.input_dict, input_file)
+            with open(filePath, 'w') as input_file:
+                yaml.safe_dump(self.input_dict, input_file, sort_keys=False)
```
Additionally, normalize values before save (e.g. convert numpy scalars to Python `float/int`, tuples to lists, sets to sorted lists) to preserve compatibility.

**Duplicate check**
Searched refreshed issues (open+closed, through #129 context / refreshed this session) via `scripts/search_issues.py` for `yaml.dump`, `python/object`, `safe_load` usage patterns — no matching issue found for unsafe-dump vs safe-load round-trip failure. (Not #96/#67/#69; #99 mentions yaml.dump/safe_load only as dependency usage context.)

**Logs / proof**
- `evidence/logs/trackI_yaml_dump_safe_load.txt`
