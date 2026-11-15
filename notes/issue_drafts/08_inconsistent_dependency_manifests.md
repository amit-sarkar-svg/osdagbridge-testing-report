# [Docs/Packaging] Inconsistent dependency declarations across `pyproject.toml`, `requirements.txt`, and `environment.yml`

**Filed:** [Nidhikhare12/OsdagBridge#100](https://github.com/Nidhikhare12/OsdagBridge/issues/100) — open (filed 2026-11-15)

**Environment**
- OsdagBridge `dev` @ `d74f56d` (2026-07-26)
- Finding type: **T6 (documentation/packaging consistency)**

**Description**
The repository provides three dependency/install manifests (`pyproject.toml`, `requirements.txt`, `environment.yml`) that declare different package sets. This inconsistency makes installs and contributor setups ambiguous and increases the chance of broken or partially working environments (especially given that actual runtime requirements also differ; see related install issues).

**Observed declarations (as read from the repo)**

**`pyproject.toml` `[project].dependencies`**
```toml
scipy>=1.10.1
fiona
shapely
pydantic>=2.0
matplotlib>=3.5
openseespy>=3.2.2.6
opsvis>=1.0
xarray
```

**`requirements.txt`**
```text
PySide6>=6.5.0,<=6.9.3
numpy>=1.21.0
scipy>=1.10.1
fiona
shapely
pydantic
xarray
ifcopenshell
openpyxl
```

**`environment.yml` (summary)**
- conda: `osdag::osdag`, `matplotlib`, `fiona`, `shapely`, `scipy>=1.10.1`, `pydantic`, `xarray`, `python>=3.11,<3.13`, `pip`
- pip: `openseespy>=3.2.2.6`, `opsvis`, `-e .`

**Inconsistencies (examples)**
- `PySide6`, `numpy`, `ifcopenshell`, `openpyxl` appear in `requirements.txt` but not in `pyproject.toml` deps.
- `matplotlib`, `openseespy`, `opsvis` appear in `pyproject.toml`/env but are missing from `requirements.txt` (and matplotlib not in requirements).
- `osdag_core` / `PyYAML` / `navcube` / `OCC` / `plotly` / `pandas` are used in source (see related finding) but are not consistently represented across manifests.
- `environment.yml` relies on `osdag::osdag` and `-e .` (with its own dep set), diverging from both `requirements.txt` and `pyproject.toml`.

**Expected behavior**
Install/dependency manifests should be consistent, clearly scoped (runtime vs dev/test vs optional extras vs conda), and aligned with the project’s actual requirements and documented install paths.

**Actual behavior**
Three manifests disagree on core/runtime packages, creating conflicting guidance for users and contributors.

**Impact**
- Users following different install instructions may get different, incomplete, or conflicting environments.
- Harder to reproduce bugs and to reason about which dependencies are truly required.

**Suggested fix**
- Establish a single source of truth for dependencies (e.g. `pyproject.toml` with optional extras) and generate/align `requirements`/conda environment from it where possible.
- Clearly document which manifest to use for which workflow (pip editable install, conda env, dev/test), and ensure each includes the packages needed for that workflow.
- Address the underlying missing/unused dependency issues (see related reports on `pyproject.toml` deps and `osdag_core` metadata).

**Duplicate check**
Searched existing OsdagBridge issues (open+closed, full titles/bodies) for `requirements.txt` / manifest-inconsistency packaging terms — no matching issue found (`environment.yml` appears only as environment context in unrelated issues). (Not #96.)
