# [Bug/Install] `osdag_core` dependency metadata declares bogus `sqlite` package (breaks clean dependency resolution)

**Filed:** [Nidhikhare12/OsdagBridge#98](https://github.com/Nidhikhare12/OsdagBridge/issues/98) — open (filed 2026-11-15)

**Environment**
- OsdagBridge `dev` @ `d74f56d` (2026-07-26), tested in conda env `osdagbridge-env` (Python 3.12.16)
- Observed in installed dependency: `osdag_core 0.0.0`
- Finding type: **T5 (installation/environment blocker)**

**Description**
The installed `osdag_core` package used with OsdagBridge declares `sqlite` as a runtime dependency in its package metadata. `sqlite` is not a valid/installable PyPI distribution for Python’s stdlib database module (the stdlib module is `sqlite3`), so this can break dependency resolution in clean environments.

**Steps to reproduce (environment/metadata check)**
1. In the OsdagBridge environment, inspect `osdag_core` metadata:
   ```python
   import importlib.metadata as m
   print(m.distribution("osdag_core").metadata.get_all("Requires-Dist"))
   ```
2. (Optional) `pip index versions sqlite` → no matching distribution.

**Expected behavior**
Dependency metadata should reference installable distributions only; stdlib `sqlite3` should not be declared as a pip package dependency.

**Actual behavior**
`osdag_core 0.0.0` `Requires-Dist` includes a bogus `sqlite` entry:
```
['pylatex', 'numpy', 'PyYaml', 'Click', 'pandas', 'sqlite', 'PySide6']
```
(evidence: `evidence/logs/phase1_installed_meta.txt`; `tests/test_phase1_packaging.py::test_osdag_core_declares_bogus_sqlite_dep`)

**Impact**
Can cause `pip`/resolver failures in fresh installs of the OsdagBridge stack (install-time blocker), depending on how dependencies are resolved.

**Suggested fix**
- If this is declared in `osdag_core` packaging: remove `sqlite` from `Requires-Dist` (stdlib `sqlite3` needs no pip dependency), or replace with the correct external package only if a non-stdlib one is actually required.
- If the pin/source of `osdag_core` is controlled by OsdagBridge setup (`environment.yml` / install docs), ensure a corrected `osdag_core` build is referenced.

**Duplicate check**
Searched existing OsdagBridge issues (open+closed, full titles/bodies) for `sqlite`/`osdag_core` dependency-metadata terms — no matching packaging issue found (hits were unrelated DB/design issues such as #20/#42). (Not #96.)

**Notes**
Observed in the installed `osdag_core` dependency metadata in the test environment (not a source change in the OsdagBridge repo itself); reporting here as an OsdagBridge-ecosystem install blocker encountered during setup/testing.
