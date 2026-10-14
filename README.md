# CampusFlow

CampusFlow is an academic administration dashboard and automated timetable scheduling engine built for colleges and universities.

## Tech Stack
- **Frontend**: React + TypeScript + Vite, styled with custom dark glassmorphism and violet/cyan accents.
- **Backend**: Python + FastAPI, housing the deterministic scheduling and hard-constraint validation engine.
- **Persistence**: In-memory demo store with Supabase PostgreSQL fallback support.

---

## Getting Started

### 1. Start the Backend API
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
API documentation is available at `http://localhost:8000/docs`.

### 2. Start the Frontend Dashboard
```bash
cd frontend
pnpm install
pnpm dev --host 0.0.0.0 --port 5173
```
Open `http://localhost:5173` in your browser.

---

## Features
- **Dashboard & Statistics**: Real-time overview of departments, rooms, faculty, subjects, sections, and scheduling status.
- **Entity Management (CRUD)**: Manage departments, rooms, faculty, subjects, and student cohorts.
- **Automated Scheduling Engine**: Greedy deterministic allocation algorithm respecting hard constraints and soft preferences.
- **Hard-Constraint Validation**: Prevents faculty, room, and section double-booking, enforces room capacity, equipment requirements, faculty qualifications, and availability windows.
- **Unscheduled Session Reporting**: Explains why sessions could not be scheduled with human-readable constraint violation reasons instead of forcing invalid assignments.
- **Weekly Timetable Grid**: Visual 30-minute slot timetable grid with filtering and conflict indicator highlights.
