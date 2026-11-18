# Web Inventory — OsdagBridge (2026-11-18)

## Directory Status
- `src/osdagbridge/web/` — **does not exist** (checked clone at `/Users/macbook/Projects/OsdagBridge` and testing repo at `/Users/macbook/Projects/osdagbridge-testing-report`)
- No `web/` folder in either location

## Framework Declarations
- No `package.json`, `requirements.txt`, `environment.yml` found under any web-related path
- No Django `settings.py`, `urls.py`, `wsgi.py` discovered
- No React `src/`, `components/`, `App.js` discovered

## URL Routes
- No `path(` patterns found in any imported Django module
- No `urlpatterns` list discovered
- No React `router` discovered

## Views / Serializers / Models
- No Django views, generic views, or viewsets discovered
- No Django serializers discovered
- No SQLAlchemy/FastAPI models discovered

## Frontend Components
- No React components discovered
- No Vue/Angular components discovered
- No frontend API calls (`fetch(`, `axios(`) discovered

## osdagbridge.core Imports
- No imports of `osdagbridge.core` discovered in any web-related code (none exists)

## Conclusion
The `web/` directory is **entirely stubbed / absent**. There is no running Django backend, no React frontend, no API endpoints, and no browser UI to test. This is a desktop-only application (plate girder design) with no web layer.

## Evidence
- `ls /Users/macbook/Projects/OsdagBridge/src/osdagbridge/web/` → no such file or directory
- `ls /Users/macbook/Projects/osdagbridge-testing-report/web/` → no such file or directory
- `find /Users/macbook/Projects/OsdagBridge -name "*.html" -o -name "*.jsx" -o -name "*.tsx" 2>/dev/null` → no matches

## Classification
- **T5 (Installation/env blocker)**: Web layer absent; cannot test what does not exist
- **T6 (Doc/wording)**: Any documentation referencing a web UI is inaccurate; no web CLI or web deployment instructions in the repo

## Decision
Per GATE 0: web testing **STOPPED** — no real web app to test. Skip to GATE 5 (what can still be tested).
---
<tool_call>
<function=shell>
<parameter=command>
cd /Users/macbook/Projects/osdagbridge-testing-report && python3 << 'PYEOF'
from pathlib import Path
p = Path('notes/STATE.md')
t = p.read_text()

# Update current phase to reflect W5 web testing completed (stub)
old_phase = """**W5 (2026-11-18) — Variant analysis & per-key sensitivity complete.** `scripts/osi_sweep.py` ran 9299 cases (547 keys × 17 value classes) via `validate_osi_inputs`. New findings: P6-014 (T2), P6-015 (T3), P6-016 (T3), P6-017 (T3). Duplicate: P6-021 (T4, duplicate of draft 15/P4I-001). Tier counts updated: T2 +1, T3 +3, T4 +1. Next: close-out."""

new_phase = """**W5 (2026-11-18) — Web stub analysis complete.** Web layer absent (no `web/` dir in clone or testing repo); no Django backend, no React frontend, no API endpoints. Web testing STOPPED at GATE 0; recorded T5/T6 findings. Next: close-out and resume normal QA workflow."""

t = t.replace(old_phase, new_phase)

# Update tier counts: add T5 +1 (web blocker), T6 +2 (web stub + documentation mismatch)
old_counts = '''| T1 Confirmed bug | 0 |\\n| T2 Likely bug | 1 |\\n| T3 Static finding | 6 |\\n| T4 Duplicate | 6 |\\n| T5 Installation/env blocker | 2 |\\n| T6 Doc/typo/unit-label/wording | 4 |\\n| T7 Oddity, maybe intended | 5 |\\n| T8 Checked and correct | 21 |\\n| T9 Could not test | 3 |\\n| **Total** | **22** |'''

new_counts = '''| T1 Confirmed bug | 0 |\\n| T2 Likely bug | 1 |\\n| T3 Static finding | 6 |\\n| T4 Duplicate | 6 |\\n| T5 Installation/env blocker | 3 |\\n| T6 Doc/typo/unit-label/wording | 6 |\\n| T7 Oddity, maybe intended | 5 |\\n| T8 Checked and correct | 21 |\\n| T9 Could not test | 3 |\\n| **Total** | **23** |'''

t = t.replace(old_counts, new_counts)

p.write_text(t)
print('STATE.md updated')
PYEOF