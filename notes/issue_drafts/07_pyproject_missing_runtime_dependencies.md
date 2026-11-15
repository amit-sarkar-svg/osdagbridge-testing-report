# [Bug/Install] `pyproject.toml` runtime dependencies omit required packages and declare unused `pydantic`

**Filed:** [Nidhikhare12/OsdagBridge#99](https://github.com/Nidhikhare12/OsdagBridge/issues/99) — open (filed 2026-11-15)

**Environment**
- OsdagBridge `dev` @ `d74f56d` (2026-07-26)
- macOS (Intel), conda env `osdagbridge-env`, Python 3.12.16
- Finding type: **T5 (installation/environment blocker)**

**Description**
`pyproject.toml` declares a runtime dependency set that does not cover several packages directly imported/used by the source, while declaring `pydantic` with no observed imports in `src`. Because `README.md` instructs installation via `pip install -e .`, the declared metadata alone is insufficient for a working install of the affected features (desktop UI, CAD/plots, IFC/export, etc.).

**Declared dependencies (`pyproject.toml`)**
```toml
dependencies = [
  "scipy>=1.10.1",
  "fiona",
  "shapely",
  "pydantic>=2.0",
  "matplotlib>=3.5",
  "openseespy>=3.2.2.6",
  "opsvis>=1.0",
  "xarray",
]
```

**Used in source but omitted from `pyproject.toml` (examples with file:line)**
| Package | Example usage in `src` | Notes |
|---|---|---|
| PySide6 | `src/osdagbridge/desktop/ui/cad_3d.py:12` `from PySide6.QtWidgets import (` | 185 imports total (desktop UI) |
| numpy | `src/ospgrillage/mesh.py:10` `import numpy as np` | core/analysis usage |
| osdag_core | `src/osdagbridge/core/utils/connect.py:31` `from osdag_core.cli import _get_output_dictionary` | direct import |
| PyYAML (`yaml`) | `src/osdagbridge/desktop/ui/template_page.py:812` `yaml.dump(...)`, `:839` `yaml.safe_load(f)` | OSI save/load |
| navcube | `src/osdagbridge/desktop/ui/utils/custom_3dviewer.py:13` `from navcube import NavCubeOverlay, NavCubeStyle` | 3D/navigation UI |
| pythonocc-core (`OCC`) | `src/osdagbridge/core/bridge_types/plate_girder/cad_generator.py:26` `from OCC.Core.Quantity import ...` | CAD (80 imports total) |
| plotly | `src/osdagbridge/core/bridge_types/plate_girder/plots_widget.py:2` `import plotly.graph_objects as go` | plots |
| ifcopenshell | `src/osdagbridge/core/ifc_export_bridge/bridge_ifc_generator.py:7` `import ifcopenshell` | IFC export |
| openpyxl | `src/osdagbridge/desktop/ui/dialogs/generate_results_dialog.py:1` `import openpyxl` | results export |
| pandas | `src/osdagbridge/core/utils/codes/is800_2007.py:12` `import pandas as pd` | data handling |

(Evidence: `evidence/logs/phase1_imports_clean.txt`, `evidence/logs/phase1_p1_002_proof.txt`, `evidence/logs/phase1_dep_grep.txt`.)

**Declared but not observed in `src`**
- `pydantic>=2.0` — `grep -rn "pydantic" src` finds only `src/osdagbridge.egg-info/*` metadata, with no source imports.

**Expected behavior**
`pyproject.toml` runtime dependencies should reflect packages required to import/run the module and its supported features (or clearly separate optional extras), so `pip install -e .` produces a usable install as documented.

**Actual behavior**
Multiple directly imported/used packages are omitted from `[project].dependencies`, and `pydantic` is declared without observed use in `src`. A `pip install -e .` install (per `README.md`) will miss required dependencies for affected functionality.

**Impact**
Fresh pip-based installs can fail at import/runtime for desktop, CAD/OCC, plotting, IFC/export, OSI I/O, and other features despite following documented installation steps.

**Suggested fix**
- Add the missing runtime dependencies (and/or define appropriate `[project.optional-dependencies]` extras for GUI/CAD/IFC/reporting) so declared metadata matches actual requirements.
- Reconcile `pydantic`: remove if unused, or document/implement its intended use.
- Align `pyproject.toml` with the other install manifests and README (related: `requirements.txt` / `environment.yml` are currently inconsistent; see separate packaging-consistency finding).

**Duplicate check**
Searched existing OsdagBridge issues (open+closed, full titles/bodies) for `pyproject`, `PySide6` (packaging), `pydantic`, and dependency-metadata terms — no matching issue found (e.g. #25 mentions PySide6 in a different context). (Not #96.)

**Notes**
Some omitted packages are feature-specific (desktop/IFC/plots/export) but are direct source imports; `pylatex` was not directly imported in `src` and is not claimed here.
