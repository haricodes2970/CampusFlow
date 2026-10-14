from typing import List, Dict, Set, Tuple, Optional
from collections import defaultdict
import random
from .models import (
    Department, Room, Faculty, Subject, Section, Session,
    Timetable, UnscheduledSession, ConstraintViolation,
    DayOfWeek, SubjectRequirement, Availability, Equipment
)


SLOT_DURATION_MINUTES = 30
SLOTS_PER_DAY = 24  # 12 hours = 24 half-hour slots
DAYS = list(DayOfWeek)


def time_to_slot(time_str: str) -> int:
    """Convert HH:MM to slot index."""
    h, m = map(int, time_str.split(":"))
    return h * 2 + (m // 30)


def slot_to_time(slot: int) -> str:
    """Convert slot index to HH:MM."""
    h = slot // 2
    m = (slot % 2) * 30
    return f"{h:02d}:{m:02d}"


def get_faculty_available_slots(faculty: Faculty) -> Set[Tuple[DayOfWeek, int]]:
    """Get all available slots for a faculty member."""
    slots = set()
    for avail in faculty.availability:
        start = time_to_slot(avail.start_time)
        end = time_to_slot(avail.end_time)
        for slot in range(start, end):
            slots.add((avail.day, slot))
    return slots


def is_faculty_available(faculty: Faculty, day: DayOfWeek, start_slot: int, duration_slots: int) -> bool:
    """Check if faculty is available for the entire session duration."""
    if not faculty.availability:
        return True  # No constraints = always available
    available_slots = get_faculty_available_slots(faculty)
    for s in range(start_slot, start_slot + duration_slots):
        if (day, s) not in available_slots:
            return False
    return True


def get_conflicts(
    sessions: List[Session],
    new_session: Session,
    rooms: Dict[str, Room],
    faculty_map: Dict[str, Faculty],
    sections: Dict[str, Section],
) -> List[ConstraintViolation]:
    """Check all hard constraints for a new session."""
    violations = []
    
    for existing in sessions:
        # Same day and overlapping time
        if existing.day != new_session.day:
            continue
        
        existing_end = existing.start_slot + existing.duration_slots
        new_end = new_session.start_slot + new_session.duration_slots
        
        # Check overlap
        if not (new_session.start_slot >= existing_end or new_session.start_slot + new_session.duration_slots <= existing.start_slot):
            # Faculty conflict
            if existing.faculty_id == new_session.faculty_id:
                violations.append(ConstraintViolation(
                    type="FACULTY_CONFLICT",
                    message=f"Faculty already scheduled at this time",
                    entity_id=new_session.faculty_id,
                    entity_type="Faculty"
                ))
            
            # Room conflict
            if existing.room_id == new_session.room_id:
                violations.append(ConstraintViolation(
                    type="ROOM_CONFLICT",
                    message=f"Room already booked at this time",
                    entity_id=new_session.room_id,
                    entity_type="Room"
                ))
            
            # Section conflict
            if existing.section_id == new_session.section_id:
                violations.append(ConstraintViolation(
                    type="SECTION_CONFLICT",
                    message=f"Student section already has a class at this time",
                    entity_id=new_session.section_id,
                    entity_type="Section"
                ))
    
    return violations


def validate_session_constraints(
    session: Session,
    rooms: Dict[str, Room],
    faculty_map: Dict[str, Faculty],
    subjects: Dict[str, Subject],
    sections: Dict[str, Section],
    existing_sessions: List[Session],
) -> List[ConstraintViolation]:
    """Validate all hard constraints for a session."""
    violations = []
    
    room = rooms.get(session.room_id)
    faculty = faculty_map.get(session.faculty_id)
    subject = subjects.get(session.subject_id)
    section = sections.get(session.section_id)
    
    if not room or not faculty or not subject or not section:
        violations.append(ConstraintViolation(
            type="MISSING_ENTITY",
            message="Referenced entity not found",
            entity_id=session.id,
            entity_type="Session"
        ))
        return violations
    
    # Room capacity
    if room.capacity < section.student_count:
        violations.append(ConstraintViolation(
            type="CAPACITY_EXCEEDED",
            message=f"Room capacity ({room.capacity}) < section size ({section.student_count})",
            entity_id=room.id,
            entity_type="Room"
        ))
    
    # Faculty qualification
    if subject.qualified_faculty_ids and faculty.id not in subject.qualified_faculty_ids:
        violations.append(ConstraintViolation(
            type="FACULTY_UNQUALIFIED",
            message=f"Faculty not qualified for this subject",
            entity_id=faculty.id,
            entity_type="Faculty"
        ))
    
    # Equipment match
    missing_equipment = set(subject.required_equipment) - set(room.equipment)
    if missing_equipment:
        violations.append(ConstraintViolation(
            type="EQUIPMENT_MISSING",
            message=f"Room missing required equipment: {', '.join(e.value for e in missing_equipment)}",
            entity_id=room.id,
            entity_type="Room"
        ))
    
    # Faculty availability
    if not is_faculty_available(faculty, session.day, session.start_slot, session.duration_slots):
        violations.append(ConstraintViolation(
            type="FACULTY_UNAVAILABLE",
            message=f"Faculty not available at this time",
            entity_id=faculty.id,
            entity_type="Faculty"
        ))
    
    # Max hours per week
    faculty_hours = sum(
        s.duration_slots * SLOT_DURATION_MINUTES / 60
        for s in existing_sessions if s.faculty_id == faculty.id
    )
    new_hours = session.duration_slots * SLOT_DURATION_MINUTES / 60
    if faculty_hours + new_hours > faculty.max_hours_per_week:
        violations.append(ConstraintViolation(
            type="MAX_HOURS_EXCEEDED",
            message=f"Faculty would exceed max hours/week ({faculty.max_hours_per_week})",
            entity_id=faculty.id,
            entity_type="Faculty"
        ))
    
    # Conflict with existing sessions
    violations.extend(get_conflicts(existing_sessions, session, rooms, faculty_map, sections))
    
    return violations


def calculate_preference_score(
    session: Session,
    rooms: Dict[str, Room],
    faculty_map: Dict[str, Faculty],
    subjects: Dict[str, Subject],
    sections: Dict[str, Section],
    existing_sessions: List[Session],
) -> float:
    """Calculate soft preference score (higher = better)."""
    score = 0.0
    faculty = faculty_map.get(session.faculty_id)
    room = rooms.get(session.room_id)
    subject = subjects.get(session.subject_id)
    section = sections.get(session.section_id)
    
    if not all([faculty, room, subject, section]):
        return -1000.0
    
    # Prefer same building for consecutive sessions
    same_section_sessions = [s for s in existing_sessions if s.section_id == session.section_id and s.day == session.day]
    for s in same_section_sessions:
        other_room = rooms.get(s.room_id)
        if other_room and other_room.building == room.building:
            score += 10
    
    # Prefer faculty's preferred times (if availability is restrictive, prefer middle)
    if faculty.availability:
        for avail in faculty.availability:
            if avail.day == session.day:
                start = time_to_slot(avail.start_time)
                end = time_to_slot(avail.end_time)
                mid = (start + end) / 2
                session_mid = session.start_slot + session.duration_slots / 2
                # Closer to middle of availability window = better
                score += max(0, 20 - abs(session_mid - mid) * 2)
    
    # Load balancing - prefer days with fewer sessions for this section
    section_day_count = sum(1 for s in existing_sessions if s.section_id == session.section_id and s.day == session.day)
    score -= section_day_count * 5
    
    # Prefer rooms that just meet capacity (not wasteful)
    capacity_ratio = room.capacity / max(section.student_count, 1)
    if 1.0 <= capacity_ratio <= 1.5:
        score += 15
    elif capacity_ratio > 2.0:
        score -= 10
    
    return score


def generate_timetable(
    departments: List[Department],
    rooms: List[Room],
    faculty: List[Faculty],
    subjects: List[Subject],
    sections: List[Section],
) -> Timetable:
    """Generate a deterministic timetable using greedy algorithm with backtracking."""
    
    # Build lookup maps
    rooms_map = {r.id: r for r in rooms}
    faculty_map = {f.id: f for f in faculty}
    subjects_map = {s.id: s for s in subjects}
    sections_map = {s.id: s for s in sections}
    rooms_by_dept = defaultdict(list)
    for r in rooms:
        rooms_by_dept[r.department_id].append(r)
    
    # Collect all required sessions
    required_sessions = []  # List of (section_id, subject_id, sessions_needed, duration_slots)
    for section in sections:
        for req in section.subject_requirements:
            required_sessions.append({
                "section_id": section.id,
                "subject_id": req.subject_id,
                "sessions_needed": req.sessions_per_week,
                "duration_slots": req.session_duration_minutes // SLOT_DURATION_MINUTES,
            })
    
    # Sort by difficulty (fewest qualified faculty, most equipment needs, largest sections)
    def session_difficulty(req):
        subject = subjects_map.get(req["subject_id"])
        section = sections_map.get(req["section_id"])
        if not subject or not section:
            return 0
        qualified_count = len([f for f in faculty if f.id in subject.qualified_faculty_ids])
        equipment_count = len(subject.required_equipment)
        return (qualified_count, -equipment_count, -section.student_count)
    
    required_sessions.sort(key=session_difficulty)
    
    scheduled_sessions: List[Session] = []
    unscheduled: List[UnscheduledSession] = []
    
    # For each required session group, try to schedule all instances
    for req in required_sessions:
        subject = subjects_map[req["subject_id"]]
        section = sections_map[req["section_id"]]
        sessions_needed = req["sessions_needed"]
        duration = req["duration_slots"]
        
        scheduled_count = 0
        violations_for_this = []
        
        # Get eligible faculty
        eligible_faculty = [f for f in faculty if f.id in subject.qualified_faculty_ids] if subject.qualified_faculty_ids else faculty
        eligible_faculty = [f for f in eligible_faculty if f.department_id == section.department_id or not f.department_id]
        
        # Get eligible rooms
        eligible_rooms = [r for r in rooms 
                         if r.capacity >= section.student_count 
                         and set(subject.required_equipment).issubset(set(r.equipment))
                         and (r.department_id == section.department_id or not r.department_id)]
        
        if not eligible_faculty or not eligible_rooms:
            violations_for_this.append(ConstraintViolation(
                type="NO_ELIGIBLE_RESOURCES",
                message="No eligible faculty or rooms for this subject/section combination",
                entity_id=subject.id,
                entity_type="Subject"
            ))
        
        # Try to schedule each session instance
        for instance in range(sessions_needed):
            best_session: Optional[Session] = None
            best_score = -float('inf')
            best_violations: List[ConstraintViolation] = []
            
            # Try all day/slot/faculty/room combinations
            for day in DAYS:
                for start_slot in range(0, SLOTS_PER_DAY - duration + 1):
                    for fac in eligible_faculty:
                        for rm in eligible_rooms:
                            candidate = Session(
                                subject_id=subject.id,
                                faculty_id=fac.id,
                                room_id=rm.id,
                                section_id=section.id,
                                day=day,
                                start_slot=start_slot,
                                duration_slots=duration
                            )
                            
                            violations = validate_session_constraints(
                                candidate, rooms_map, faculty_map, subjects_map, sections_map, scheduled_sessions
                            )
                            
                            if not violations:
                                score = calculate_preference_score(
                                    candidate, rooms_map, faculty_map, subjects_map, sections_map, scheduled_sessions
                                )
                                if score > best_score:
                                    best_score = score
                                    best_session = candidate
                                    best_violations = []
                            elif not best_session and not violations_for_this:
                                # Track violations for unscheduled reporting
                                best_violations = violations
            
            if best_session:
                scheduled_sessions.append(best_session)
                scheduled_count += 1
            else:
                # Could not schedule this instance
                violations_for_this.extend(best_violations)
                break
        
        if scheduled_count < sessions_needed:
            unscheduled.append(UnscheduledSession(
                subject_id=subject.id,
                section_id=section.id,
                subject_name=subject.name,
                section_name=section.name,
                required_sessions=sessions_needed,
                scheduled_sessions=scheduled_count,
                violations=violations_for_this
            ))
    
    return Timetable(sessions=scheduled_sessions, unscheduled=unscheduled)