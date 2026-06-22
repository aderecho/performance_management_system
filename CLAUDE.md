# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Performance Management System (PME)** — a hierarchical planning, monitoring, and reporting platform for organizational initiatives.

- **Backend:** Django 5.2 + Django REST Framework, PostgreSQL, Python 3.12 (`perf-mgt-be/`)
- **Frontend:** Quasar Framework v2 (Vue 3), Vite, Node.js (`perf-mgt-fe/`)
- **Auth:** JWT tokens delivered via HTTP-only cookies

## Development Commands

### Backend (`perf-mgt-be/`)
```bash
python manage.py runserver 0.0.0.0:8000
python manage.py makemigrations --name meaningful_name
python manage.py migrate
python manage.py createsuperuser
python manage.py shell
```

### Frontend (`perf-mgt-fe/`)
```bash
npm install
npm run dev          # Quasar dev server on port 9000
npm run lint         # ESLint (flat config)
npm run format       # Prettier
npm run build        # Output to dist/spa
```

### Docker (full stack)
```bash
docker-compose -f docker-compose.dev.yml up
```
- Frontend: http://localhost:9000 | Backend: http://localhost:8000

## Architecture

### Data Model

The system uses an **Adjacency List** for hierarchical nodes:

```
Template (framework definition)
  └── Document (instance, e.g. "FY2025 Strategic Plan")
        └── Item (self-referencing: Program → Project → Activity)
              └── Initiative → InitiativeAccomplishment (evidence files)
```

Key relations:
- `Item.parent = ForeignKey(self, null=True)` — null means root node
- `Item.template_node_type` determines its level label (Program/Project/Activity)
- `ReportingPeriod` sets submission deadlines per Document
- `ItemContributor` links organizational Units to Items

### Backend Structure (`perf-mgt-be/`)

```
apps/
  authentication/   # Custom JWT + cookie auth, email-based login
  core/             # Shared models: Unit, UnitOfMeasure, User extensions
  pme/              # Business domain
    models.py       # All 9 models (Template, Document, Item, Initiative, etc.)
    serializers.py  # DRF serializers with nested relationships
    views.py        # ViewSets + custom @action decorators
    services.py     # Business logic (reporting period generation, dashboard summary)
    urls.py         # DefaultRouter + nested routes (items/<item_pk>/initiatives/)
perf_mgt/
  settings.py       # Django config, DB, JWT (15-min access / 7-day refresh), CORS
  urls.py           # Mounts /api/v1/{core,pme,auth}/
```

All API routes are versioned at `/api/v1/`.

### Frontend Structure (`perf-mgt-fe/`)

```
src/
  boot/axios.js         # Axios instance; intercepts 401s and refreshes token automatically
  router/               # Vue Router; beforeEach guard redirects unauthenticated users to /login
  stores/
    auth.js             # Login/logout/session state
    config.js           # Templates and app config
    core.js             # Units, users, shared lookups
    pme/dashboard.js    # Dashboard metrics
    pme/pmeDocument.js  # Document CRUD
    pme/initiative.js   # Initiative list, filters, submission state
  pages/                # Login, Dashboard, PME editor, Admin (Users/Roles/Permissions), Audit
  components/           # Reusable Quasar-based components
```

**UI libraries:** Quasar (QTable, QDialog, etc.), Vee-Validate + Zod for forms, ECharts for charts, Lucide icons.

### Auth Flow

1. POST `/api/v1/auth/login/` → JWT tokens set in HTTP-only cookies
2. All subsequent requests include cookies automatically (Axios `withCredentials: true`)
3. On 401, Axios interceptor POSTs `/api/v1/auth/refresh/` and retries the original request
4. POST `/api/v1/auth/logout/` clears the session

## Configuration Files

| File | Purpose |
|------|---------|
| `perf-mgt-be/.env.dev` | `SECRET_KEY`, DB credentials, `ALLOWED_HOSTS`, `DEBUG` |
| `perf-mgt-be/requirements.txt` | Python deps (Django 5.2, DRF, psycopg2, djangorestframework-simplejwt) |
| `perf-mgt-fe/quasar.config.js` | Vite + Quasar build, i18n, ESLint integration |
| `perf-mgt-fe/jsconfig.json` | Path aliases (`@` → `src/`) |

## Git Conventions (from AGENTS.md)

- **Branch naming:** `feature/*`, `fix/*`, `refactor/*`, `chore/*`
- **Commits:** `type(scope): description` — e.g., `feat(pme): add initiative filters`
- Never hardcode secrets; use environment variables

## Known Technical Debt

The Item model uses an Adjacency List. A future refactor to **Modified Preorder Tree Traversal (MPTT)** or **Closure Table** is noted in `pme/models.py` comments for better deep-hierarchy query performance.
