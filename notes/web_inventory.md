# Web Inventory — OsdagBridge (2026-11-18, corrected)

**Correction (2026-11-18):** the earlier W5 inventory checked `src/osdagbridge/web/` and the testing repo's `web/`; the actual stub lives at the **repo root** `web/`. Verified with `find /Users/macbook/Projects/OsdagBridge/web -type f`:

| File | Content | Verdict |
|---|---|---|
| `web/backend/manage.py` | `#!/usr/bin/env python` + `print("Django manage stub")` | stub — no Django project |
| `web/frontend/package.json` | `{"name":"osdagbridge-frontend","version":"0.0.0"}` only | stub — no scripts, no deps |
| `web/frontend/src/App.jsx` | `export default function App(){ return null; }` | placeholder — renders nothing |
| `web/frontend/src/components/.gitkeep` | `# placeholder` | empty components dir |
| `web/.DS_Store` | 6148 bytes (macOS artifact) | noise |

- No `settings.py`, `urls.py`, `wsgi.py`, Django apps, models, views, or serializers anywhere (no `urlpatterns` in the tree).
- No `package-lock.json` entry worth nothing — it exists but declares nothing for the app (frontend is unbuildable; `npm install` would give nothing).
- No `fetch(`/`axios(` call sites; no imports of `osdagbridge.core` under `web/`.

**Conclusion:** web layer is **stub-only**. There is no Django backend, no React frontend, no API endpoints — testing a web UI cannot start. This confirms the earlier Phase 1 finding P1-007 and matches issue #155's conclusion (web application layer absent), though #155's "top-level web directory — Not found" claim is inaccurate (the directory exists but only holds stubs).

**Classification:** T5 (testing-scope blocker) + T6 (documentation/scope mismatch). Earlier reclassified to T4 (duplicate of #155) on 2026-11-18.

**Evidence commands (read-only):**
- `find /Users/macbook/Projects/OsdagBridge/web -type f`
- `cat web/backend/manage.py web/frontend/package.json web/frontend/src/App.jsx`
- `grep -rn "urlpatterns" /Users/macbook/Projects/OsdagBridge --include=*.py`
