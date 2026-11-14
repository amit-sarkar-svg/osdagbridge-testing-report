# Setup Log (macOS Intel)
1. Assignment step 11 (cd osdagbridge/src) fails: real layout is src/osdagbridge.
2. PySide6 was missing after conda env create; installed with pip (6.11.3).
3. Qt "cocoa" platform plugin error: FILL IN what fixed it.
4. Design failed with "No module named osdag_core" (connect.py:31). The osdag 2025.01.a.2 package from environment.yml lacks it. Newer osdag versions need osdag_latex_env, which is not available in the listed channels.
5. Workaround: cloned osdag-core. "pip install -e ." failed ("No matching distribution found for sqlite"), so I used "pip install --no-deps -e .".
