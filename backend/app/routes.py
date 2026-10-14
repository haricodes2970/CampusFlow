from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from app.models import (
    Department, Room, Faculty, Subject, Section, Session,
    Timetable, UnscheduledSession, DayOfWeek, Equipment, Availability, SubjectRequirement,
    ConstraintViolation
)
from app.scheduler import (
    generate_timetable, validate_session_constraints, calculate_preference_score,
    time_to_slot, slot_to_time
)
from app.database import store

router = APIRouter()


# Health check
@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "campusflow-backend"}


# Departments
@router.get("/departments", response_model=List[Department])
async def list_departments():
    return store.departments


@router.post("/departments", response_model=Department)
async def create_department(dept: Department):
    store.departments.append(dept)
    return dept


@router.get("/departments/{dept_id}", response_model=Department)
async def get_department(dept_id: str):
    dept = next((d for d in store.departments if d.id == dept_id), None)
    if not dept:
        raise HTTPException(404, "Department not found")
    return dept


@router.put("/departments/{dept_id}", response_model=Department)
async def update_department(dept_id: str, dept: Department):
    idx = next((i for i, d in enumerate(store.departments) if d.id == dept_id), None)
    if idx is None:
        raise HTTPException(404, "Department not found")
    store.departments[idx] = dept
    return dept


@router.delete("/departments/{dept_id}")
async def delete_department(dept_id: str):
    store.departments = [d for d in store.departments if d.id != dept_id]
    return {"ok": True}


# Rooms
@router.get("/rooms", response_model=List[Room])
async def list_rooms():
    return store.rooms


@router.post("/rooms", response_model=Room)
async def create_room(room: Room):
    store.rooms.append(room)
    return room


@router.get("/rooms/{room_id}", response_model=Room)
async def get_room(room_id: str):
    room = next((r for r in store.rooms if r.id == room_id), None)
    if not room:
        raise HTTPException(404, "Room not found")
    return room


@router.put("/rooms/{room_id}", response_model=Room)
async def update_room(room_id: str, room: Room):
    idx = next((i for i, r in enumerate(store.rooms) if r.id == room_id), None)
    if idx is None:
        raise HTTPException(404, "Room not found")
    store.rooms[idx] = room
    return room


@router.delete("/rooms/{room_id}")
async def delete_room(room_id: str):
    store.rooms = [r for r in store.rooms if r.id != room_id]
    return {"ok": True}


# Faculty
@router.get("/faculty", response_model=List[Faculty])
async def list_faculty():
    return store.faculty


@router.post("/faculty", response_model=Faculty)
async def create_faculty(fac: Faculty):
    store.faculty.append(fac)
    return fac


@router.get("/faculty/{faculty_id}", response_model=Faculty)
async def get_faculty(faculty_id: str):
    fac = next((f for f in store.faculty if f.id == faculty_id), None)
    if not fac:
        raise HTTPException(404, "Faculty not found")
    return fac


@router.put("/faculty/{faculty_id}", response_model=Faculty)
async def update_faculty(faculty_id: str, fac: Faculty):
    idx = next((i for i, f in enumerate(store.faculty) if f.id == faculty_id), None)
    if idx is None:
        raise HTTPException(404, "Faculty not found")
    store.faculty[idx] = fac
    return fac


@router.delete("/faculty/{faculty_id}")
async def delete_faculty(faculty_id: str):
    store.faculty = [f for f in store.faculty if f.id != faculty_id]
    return {"ok": True}


# Subjects
@router.get("/subjects", response_model=List[Subject])
async def list_subjects():
    return store.subjects


@router.post("/subjects", response_model=Subject)
async def create_subject(sub: Subject):
    store.subjects.append(sub)
    return sub


@router.get("/subjects/{subject_id}", response_model=Subject)
async def get_subject(subject_id: str):
    sub = next((s for s in store.subjects if s.id == subject_id), None)
    if not sub:
        raise HTTPException(404, "Subject not found")
    return sub


@router.put("/subjects/{subject_id}", response_model=Subject)
async def update_subject(subject_id: str, sub: Subject):
    idx = next((i for i, s in enumerate(store.subjects) if s.id == subject_id), None)
    if idx is None:
        raise HTTPException(404, "Subject not found")
    store.subjects[idx] = sub
    return sub


@router.delete("/subjects/{subject_id}")
async def delete_subject(subject_id: str):
    store.subjects = [s for s in store.subjects if s.id != subject_id]
    return {"ok": True}


# Sections
@router.get("/sections", response_model=List[Section])
async def list_sections():
    return store.sections


@router.post("/sections", response_model=Section)
async def create_section(sec: Section):
    store.sections.append(sec)
    return sec


@router.get("/sections/{section_id}", response_model=Section)
async def get_section(section_id: str):
    sec = next((s for s in store.sections if s.id == section_id), None)
    if not sec:
        raise HTTPException(404, "Section not found")
    return sec


@router.put("/sections/{section_id}", response_model=Section)
async def update_section(section_id: str, sec: Section):
    idx = next((i for i, s in enumerate(store.sections) if s.id == section_id), None)
    if idx is None:
        raise HTTPException(404, "Section not found")
    store.sections[idx] = sec
    return sec


@router.delete("/sections/{section_id}")
async def delete_section(section_id: str):
    store.sections = [s for s in store.sections if s.id != section_id]
    return {"ok": True}


# Timetable generation
@router.post("/timetable/generate", response_model=Timetable)
async def generate():
    store.run_generation()
    return store.timetable


@router.get("/timetable", response_model=Timetable)
async def get_timetable():
    return store.timetable


# Sessions - validated editing
class SessionCreateRequest(BaseModel):
    subject_id: str
    faculty_id: str
    room_id: str
    section_id: str
    day: DayOfWeek
    start_time: str  # HH:MM
    duration_minutes: int = 60


class SessionUpdateRequest(BaseModel):
    faculty_id: Optional[str] = None
    room_id: Optional[str] = None
    day: Optional[DayOfWeek] = None
    start_time: Optional[str] = None
    duration_minutes: Optional[int] = None


@router.post("/sessions", response_model=Session)
async def create_session(req: SessionCreateRequest):
    duration_slots = req.duration_minutes // 30
    start_slot = time_to_slot(req.start_time)
    
    new_session = Session(
        subject_id=req.subject_id,
        faculty_id=req.faculty_id,
        room_id=req.room_id,
        section_id=req.section_id,
        day=req.day,
        start_slot=start_slot,
        duration_slots=duration_slots
    )
    
    # Validate
    rooms_map = {r.id: r for r in store.rooms}
    faculty_map = {f.id: f for f in store.faculty}
    subjects_map = {s.id: s for s in store.subjects}
    sections_map = {s.id: s for s in store.sections}
    
    violations = validate_session_constraints(
        new_session, rooms_map, faculty_map, subjects_map, sections_map, store.timetable.sessions
    )
    
    if violations:
        raise HTTPException(400, detail={"violations": [v.model_dump() for v in violations]})
    
    store.timetable.sessions.append(new_session)
    return new_session


@router.get("/sessions", response_model=List[Session])
async def list_sessions():
    return store.timetable.sessions


@router.put("/sessions/{session_id}", response_model=Session)
async def update_session(session_id: str, req: SessionUpdateRequest):
    idx = next((i for i, s in enumerate(store.timetable.sessions) if s.id == session_id), None)
    if idx is None:
        raise HTTPException(404, "Session not found")
    
    session = store.timetable.sessions[idx]
    
    # Create updated session
    updated = Session(
        id=session.id,
        subject_id=session.subject_id,
        faculty_id=req.faculty_id or session.faculty_id,
        room_id=req.room_id or session.room_id,
        section_id=session.section_id,
        day=req.day or session.day,
        start_slot=time_to_slot(req.start_time) if req.start_time else session.start_slot,
        duration_slots=(req.duration_minutes // 30) if req.duration_minutes else session.duration_slots
    )
    
    # Validate against OTHER sessions (excluding self)
    other_sessions = [s for i, s in enumerate(store.timetable.sessions) if i != idx]
    rooms_map = {r.id: r for r in store.rooms}
    faculty_map = {f.id: f for f in store.faculty}
    subjects_map = {s.id: s for s in store.subjects}
    sections_map = {s.id: s for s in store.sections}
    
    violations = validate_session_constraints(
        updated, rooms_map, faculty_map, subjects_map, sections_map, other_sessions
    )
    
    if violations:
        raise HTTPException(400, detail={"violations": [v.model_dump() for v in violations]})
    
    store.timetable.sessions[idx] = updated
    return updated


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    store.timetable.sessions = [s for s in store.timetable.sessions if s.id != session_id]
    return {"ok": True}


# Statistics for dashboard
@router.get("/stats")
async def get_stats():
    return {
        "departments": len(store.departments),
        "rooms": len(store.rooms),
        "faculty": len(store.faculty),
        "subjects": len(store.subjects),
        "sections": len(store.sections),
        "scheduled_sessions": len(store.timetable.sessions),
        "unscheduled_sessions": sum(u.required_sessions - u.scheduled_sessions for u in store.timetable.unscheduled),
        "unscheduled_details": len(store.timetable.unscheduled),
    }


# Unscheduled sessions with reasons
@router.get("/timetable/unscheduled", response_model=List[UnscheduledSession])
async def get_unscheduled():
    return store.timetable.unscheduled