# CampusFlow

CampusFlow is an academic administration dashboard and automated timetable scheduling engine built for colleges and universities.

## Tech Stack
- **Frontend**: React + TypeScript + Vite, styled with custom dark glassmorphism and violet/cyan accents.
- **Backend**: Python + FastAPI, housing the deterministic scheduling and hard-constraint validation engine.
- **Database**: Supabase (PostgreSQL) with in-memory fallback for local development.
- **Deployment**: Vercel (frontend + serverless API) or any Python-compatible host + static frontend.

---

## Getting Started & Verification

### 1. Start the Backend API
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -e .
cp .env.example .env  # Edit with Supabase credentials if using DB
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
API documentation & interactive OpenAPI spec: `http://localhost:8000/docs`.

### 2. Run Automated Tests
```bash
cd backend
python -m pytest tests/ -v
```
*(All 20 constraint, scheduling, and database persistence unit tests pass successfully).*

### 3. Start the Frontend Dashboard
```bash
cd frontend
pnpm install
cp .env.example .env  # Set VITE_API_BASE if backend is on different host
pnpm dev --host 0.0.0.0 --port 5173
```
Open `http://localhost:5173` in your browser.

---

## 3-Minute Demo Walkthrough Flow

1. **Dashboard & Metrics (0:00 - 0:45)**:
   - Open `http://localhost:5173`.
   - Review live department, room, faculty, subject, and section stats.
   - Inspect the **Unscheduled Sessions & Constraint Explanations** panel to see why certain sessions could not be auto-scheduled.

2. **Core Entity Management (0:45 - 1:15)**:
   - Click on **Rooms**, **Faculty**, or **Subjects** in the sidebar.
   - View seeded demo records, edit properties (capacity, equipment), or create new records.

3. **Automated Timetable Generation (1:15 - 1:45)**:
   - Click **Generate Timetable** to run the deterministic greedy allocation engine.

4. **Hard-Constraint Validation & Conflict Feedback (1:45 - 2:30)**:
   - Go to **Timetable** view.
   - Use **Add Validated Session** to attempt an invalid session (unavailable faculty, room overcapacity).
   - Observe API rejection with structured `ConstraintViolation` reasons via toast notifications.

5. **Persistence & Limitations (2:30 - 3:00)**:
   - Note the **Local Demo Persistence Active** indicator. Changes persist in-memory; regeneration resets state.

---

## Supabase PostgreSQL Integration

### Database Schema
- Version-controlled migrations in `supabase/migrations/`:
  - `20241201_000001_initial_schema.sql` — Core tables, indexes, RLS policies
  - `20241201_000002_seed_data.sql` — Idempotent demo data seed

### Tables
| Table | Purpose |
|-------|---------|
| `colleges` | Top-level academic institutions |
| `departments` | Academic departments within colleges |
| `rooms` | Physical spaces with capacity & equipment |
| `faculty` | Instructors with qualifications & max hours |
| `faculty_availability` | Normalized weekly availability windows |
| `subjects` | Courses with equipment/capacity requirements |
| `sections` | Student cohorts |
| `section_subject_requirements` | Weekly session requirements per subject |
| `timetable_sessions` | Scheduled sessions with 30-min slot precision |

### Enabling Supabase Persistence
1. Create a Supabase project at `https://supabase.com`
2. Run migrations via Supabase SQL Editor or CLI:
   ```bash
   supabase db push
   # or copy-paste migration files into SQL Editor
   ```
3. Configure backend `.env`:
   ```env
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_ANON_KEY=your-anon-key
   SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
   CORS_ORIGINS=https://your-frontend.vercel.app,http://localhost:5173
   ```
4. Restart backend — the app automatically detects Supabase config and switches from in-memory to PostgreSQL.

### Security Notes
- Service role key **never** leaves the backend (no `VITE_` prefix)
- Row Level Security (RLS) enabled on all tables; current policies allow anon read / authenticated write
- In production, restrict policies to authenticated users with proper authorization

---

## Deployment

### Vercel (Frontend + Serverless API)
1. Push repository to GitHub
2. Import project in Vercel
3. Configure environment variables in Vercel Dashboard:
   - `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY` (backend)
   - `VITE_API_BASE` = `https://your-vercel-app.vercel.app/api` (frontend)
4. Vercel auto-detects `vercel.json` for serverless Python function routing
5. Deploy

### Alternative: Separate Hosts
- **Frontend**: Vercel / Netlify / Cloudflare Pages (static build from `frontend/dist`)
- **Backend**: Railway / Render / Fly.io / AWS / GCP (Python container/VM)
- Update `CORS_ORIGINS` in backend env to match frontend production URL

### Build Commands
```bash
# Frontend production build
cd frontend && pnpm run build

# Backend (already importable as uvicorn app.main:app)
```

---

## Environment Variables

### Backend (`backend/.env`)
| Variable | Required | Description |
|----------|----------|-------------|
| `SUPABASE_URL` | No* | Supabase project URL (enables PostgreSQL mode) |
| `SUPABASE_ANON_KEY` | No* | Supabase anon public key |
| `SUPABASE_SERVICE_ROLE_KEY` | No* | Supabase service role key (server-only) |
| `APP_HOST` | No | Server bind address (default: 0.0.0.0) |
| `APP_PORT` | No | Server port (default: 8000) |
| `DEBUG` | No | Enable debug mode (default: true) |
| `CORS_ORIGINS` | No | Comma-separated allowed origins |

*Required only for Supabase mode; otherwise in-memory fallback is used.

### Frontend (`frontend/.env`)
| Variable | Required | Description |
|----------|----------|-------------|
| `VITE_API_BASE` | No | Backend API base URL (default: http://localhost:8000/api) |

---

## Project Structure
```
CampusFlow/
├── backend/
│   ├── app/
│   │   ├── config.py          # Settings & environment
│   │   ├── database.py        # In-memory store + Supabase factory
│   │   ├── supabase_store.py  # PostgreSQL repository implementation
│   │   ├── models.py          # Pydantic domain models
│   │   ├── scheduler.py       # Deterministic scheduling engine
│   │   ├── routes.py          # FastAPI REST endpoints
│   │   └── main.py            # App entrypoint
│   ├── tests/
│   │   ├── test_scheduler.py  # 12 constraint validation tests
│   │   └── test_database.py   # 8 CRUD & persistence tests
│   ├── supabase/
│   │   └── migrations/        # Version-controlled SQL
│   ├── pyproject.toml
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/        # React views (Dashboard, Timetable, EntityManager)
│   │   ├── api.ts             # Typed API client
│   │   └── ...
│   ├── public/
│   │   ├── logo.svg           # CampusFlow brand logo
│   │   └── favicon.svg
│   ├── package.json
│   ├── vercel.json
│   └── .env.example
└── README.md
```

---

## Features & Architecture
- **Dashboard & Statistics**: Real-time overview of academic resources and scheduling coverage.
- **Entity CRUD**: Full management of departments, rooms, faculty, subjects, and student cohorts.
- **Automated Scheduling Engine**: Greedy deterministic allocation algorithm respecting hard constraints and soft preferences.
- **Hard-Constraint Validation**: Exclusivity checks (faculty, room, section), capacity enforcement, equipment matching, qualification verification, and availability windows.
- **Unscheduled Session Reporting**: Explains unscheduled sessions with human-readable constraint violation reasons instead of forcing invalid assignments.
- **Weekly Timetable Grid**: Visual 30-minute slot timetable grid (07:00–19:00) with section/day filtering and conflict indicator highlights.
- **Supabase Persistence**: Zero-config local fallback; seamless upgrade to PostgreSQL via environment variables.
- **Test Coverage**: 20 unit tests covering scheduler constraints, database CRUD, and timetable persistence.

---

## Known Limitations
- No authentication/authorization implemented (RLS policies are permissive for demo)
- Single-tenant data model; multi-college isolation not enforced at DB level
- In-memory store resets on backend restart
- Supabase migration tooling (`supabase` CLI) not configured in CI
- Frontend uses global API base; no dynamic runtime configuration beyond build-time `VITE_API_BASE`