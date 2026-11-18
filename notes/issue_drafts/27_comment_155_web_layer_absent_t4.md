# Comment draft — issue #155 (web layer absent → T4 duplicate)

**Filing:** <https://github.com/Nidhikhare12/OsdagBridge/issues/155> — "[Documentation/Scope] No Web Application Layer Found — Django Backend and React Frontend Absent" (open, 2026-11-18, filed by amit-sarkar-svg)

**Finding type:** T4 (duplicate of #155). Originally Phase 1 finding **P1-007** (T9); reclassified to T4 once #155 was filed, with a corrected inventory below.

**Corrected repository-root inventory (read-only):**

`find /Users/macbook/Projects/OsdagBridge/web -type f` → 5 files:

| File | Content | Verdict |
|---|---|---|
| `web/backend/manage.py` | `print("Django manage stub")` | stub — no Django project |
| `web/frontend/package.json` | `{"name":"osdagbridge-frontend","version":"0.0.0"}` | stub — no scripts/deps |
| `web/frontend/src/App.jsx` | `export default function App(){ return null; }` | renders nothing |
| `web/frontend/src/components/.gitkeep` | `# placeholder` | empty dir |
| `web/.DS_Store` | macOS artifact | noise |

- No `settings.py`, `urls.py`, `wsgi.py`, Django apps/models/views/serializers; no `urlpatterns` anywhere in the tree.
- No `fetch(`/`axios(` calls; no `osdagbridge.core` import under `web/`.
- `package-lock.json` present but declares nothing runnable.

**Note for the issue author:** the evidence table in #155 lists "Top-level web directory — Not found", but `/Users/macbook/Projects/OsdagBridge/web/` **does** exist at the repository root; it is stub-only. The conclusion of the issue (no Django/React layer; web testing blocked) is correct.

**Local evidence paths:**
- `notes/web_inventory.md` — corrected inventory
- `notes/all_issues_and_bugs.md` — P1-007 (reclassified T9 → T4 of #155)
- `test_log.md` — row P6-W5-05/P6-W5-08 (web stub)

**Notes:** Web testing stopped at GATE 0 per the W5 plan. If the web layer is intended, implementing it (Django backend + React frontend + API) would be needed before web QA can start; otherwise docs/requirements should state the desktop-only scope.
