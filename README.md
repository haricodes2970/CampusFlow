# CampusFlow

CampusFlow is an academic administration dashboard and automated timetable scheduling engine built for colleges and universities.

## Tech Stack
- **Frontend**: React + TypeScript + Vite, styled with custom dark glassmorphism and violet/cyan accents.
- **Backend**: Python + FastAPI, housing the deterministic scheduling and hard-constraint validation engine.
- **Persistence**: In-memory demo store with Supabase PostgreSQL integration capability (local demo fallback active).

---

## Getting Started & Verification

### 1. Start the Backend API
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -e .
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
API documentation & interactive OpenAPI spec: `http://localhost:8000/docs`.

### 2. Run Automated Scheduling Tests
```bash
cd backend
python -m pytest tests/test_scheduler.py -v
```
*(All 12 constraint and scheduling unit tests pass successfully).*

### 3. Start the Frontend Dashboard
```bash
cd frontend
pnpm install
pnpm dev --host 0.0.0.0 --port 5173
```
Open `http://localhost:5173` in your browser.

---

## 3-Minute Demo Walkthrough Flow

1. **Dashboard & Metrics (0:00 - 0:45)**:
   - Open `http://localhost:5173`.
   - Review live department, room, faculty, subject, and section stats.
   - Inspect the **Unscheduled Sessions & Constraint Explanations** panel to see why certain sessions could not be auto-scheduled (e.g. faculty availability windows or missing equipment).
2. **Core Entity Management (0:45 - 1:15)**:
   - Click on **Rooms**, **Faculty**, or **Subjects** in the sidebar.
   - View seeded demo records, edit properties (such as room capacity or equipment), or create a new department/room.
3. **Automated Timetable Generation (1:15 - 1:45)**:
   - Click **Generate Timetable** in the top bar to run the deterministic greedy allocation engine across all departmental requirements.
4. **Hard-Constraint Validation & Conflict Feedback (1:45 - 2:30)**:
   - Go to the **Timetable** view.
   - Use the **Add Validated Session** form to attempt scheduling an invalid session (e.g., booking a faculty member during their unavailable window or exceeding room capacity).
   - Observe how the API rejects the invalid change with a structured 400 error detailing the exact `ConstraintViolation` reasons (shown via toast notifications).
5. **Persistence & Limitations (2:30 - 3:00)**:
   - Note the **Local Demo Persistence Active** status indicator on the dashboard. Changes persist in memory for the running session and can be reset or regenerated instantly.

---

## Features & Architecture
- **Dashboard & Statistics**: Real-time overview of academic resources and scheduling coverage.
- **Entity CRUD**: Full management of departments, rooms, faculty, subjects, and student cohorts.
- **Automated Scheduling Engine**: Greedy deterministic allocation algorithm respecting hard constraints and soft preferences.
- **Hard-Constraint Validation**: Exclusivity checks (faculty, room, section), capacity enforcement, equipment matching, qualification verification, and availability windows.
- **Unscheduled Session Reporting**: Explains unscheduled sessions with human-readable constraint violation reasons instead of forcing invalid assignments.
- **Weekly Timetable Grid**: Visual 30-minute slot timetable grid (07:00–19:00) with section/day filtering and conflict indicator highlights.
