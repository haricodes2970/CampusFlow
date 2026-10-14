import pytest
from app.scheduler import (
    generate_timetable,
    validate_session_constraints,
    calculate_preference_score,
    time_to_slot,
    slot_to_time,
)
from app.models import (
    Department, Room, Faculty, Subject, Section,
    Session, DayOfWeek, Equipment, Availability, SubjectRequirement
)


def create_test_data():
    """Create minimal test data for scheduler tests."""
    dept = Department(id="dept-1", name="Test Dept", code="TEST", college_id="col-1")
    
    room1 = Room(id="room-1", name="Room 1", building="Main", capacity=50, equipment=[Equipment.PROJECTOR], department_id="dept-1")
    room2 = Room(id="room-2", name="Room 2", building="Main", capacity=30, equipment=[Equipment.PROJECTOR], department_id="dept-1")
    
    fac1 = Faculty(
        id="fac-1", name="Faculty 1", email="f1@test.com",
        qualifications=["CS"], max_hours_per_week=20,
        availability=[Availability(day=DayOfWeek.MONDAY, start_time="09:00", end_time="17:00")],
        department_id="dept-1"
    )
    fac2 = Faculty(
        id="fac-2", name="Faculty 2", email="f2@test.com",
        qualifications=["CS"], max_hours_per_week=20,
        availability=[Availability(day=DayOfWeek.MONDAY, start_time="09:00", end_time="17:00")],
        department_id="dept-1"
    )
    
    sub1 = Subject(
        id="sub-1", code="CS101", name="Intro to CS",
        required_equipment=[Equipment.PROJECTOR], min_room_capacity=20,
        qualified_faculty_ids=["fac-1", "fac-2"], department_id="dept-1"
    )
    
    sec1 = Section(
        id="sec-1", name="Section A", student_count=25, department_id="dept-1",
        subject_requirements=[SubjectRequirement(subject_id="sub-1", sessions_per_week=2, session_duration_minutes=60)]
    )
    
    return [dept], [room1, room2], [fac1, fac2], [sub1], [sec1]


def test_time_to_slot():
    assert time_to_slot("09:00") == 18
    assert time_to_slot("09:30") == 19
    assert time_to_slot("10:00") == 20
    assert time_to_slot("17:00") == 34
    assert time_to_slot("00:00") == 0


def test_slot_to_time():
    assert slot_to_time(18) == "09:00"
    assert slot_to_time(19) == "09:30"
    assert slot_to_time(20) == "10:00"
    assert slot_to_time(34) == "17:00"
    assert slot_to_time(0) == "00:00"


def test_generate_timetable_basic():
    depts, rooms, faculty, subjects, sections = create_test_data()
    timetable = generate_timetable(depts, rooms, faculty, subjects, sections)
    
    # Should schedule 2 sessions for the subject
    assert len(timetable.sessions) == 2
    assert len(timetable.unscheduled) == 0
    
    # Verify no overlaps
    for i, s1 in enumerate(timetable.sessions):
        for s2 in timetable.sessions[i+1:]:
            if s1.day == s2.day:
                s1_end = s1.start_slot + s1.duration_slots
                s2_end = s2.start_slot + s2.duration_slots
                assert not (s1.start_slot < s2_end and s2.start_slot < s1_end), "Sessions overlap"


def test_faculty_conflict_prevention():
    depts, rooms, faculty, subjects, sections = create_test_data()
    
    # Manually create a session
    rooms_map = {r.id: r for r in rooms}
    faculty_map = {f.id: f for f in faculty}
    subjects_map = {s.id: s for s in subjects}
    sections_map = {s.id: s for s in sections}
    
    # First session at Monday 09:00
    session1 = Session(
        subject_id="sub-1", faculty_id="fac-1", room_id="room-1",
        section_id="sec-1", day=DayOfWeek.MONDAY, start_slot=18, duration_slots=2
    )
    
    # Second session with same faculty at same time should fail
    session2 = Session(
        subject_id="sub-1", faculty_id="fac-1", room_id="room-2",
        section_id="sec-1", day=DayOfWeek.MONDAY, start_slot=18, duration_slots=2
    )
    
    violations = validate_session_constraints(session2, rooms_map, faculty_map, subjects_map, sections_map, [session1])
    assert any(v.type == "FACULTY_CONFLICT" for v in violations)


def test_room_conflict_prevention():
    depts, rooms, faculty, subjects, sections = create_test_data()
    
    rooms_map = {r.id: r for r in rooms}
    faculty_map = {f.id: f for f in faculty}
    subjects_map = {s.id: s for s in subjects}
    sections_map = {s.id: s for s in sections}
    
    session1 = Session(
        subject_id="sub-1", faculty_id="fac-1", room_id="room-1",
        section_id="sec-1", day=DayOfWeek.MONDAY, start_slot=18, duration_slots=2
    )
    
    session2 = Session(
        subject_id="sub-1", faculty_id="fac-2", room_id="room-1",
        section_id="sec-1", day=DayOfWeek.MONDAY, start_slot=18, duration_slots=2
    )
    
    violations = validate_session_constraints(session2, rooms_map, faculty_map, subjects_map, sections_map, [session1])
    assert any(v.type == "ROOM_CONFLICT" for v in violations)


def test_section_conflict_prevention():
    depts, rooms, faculty, subjects, sections = create_test_data()
    
    rooms_map = {r.id: r for r in rooms}
    faculty_map = {f.id: f for f in faculty}
    subjects_map = {s.id: s for s in subjects}
    sections_map = {s.id: s for s in sections}
    
    session1 = Session(
        subject_id="sub-1", faculty_id="fac-1", room_id="room-1",
        section_id="sec-1", day=DayOfWeek.MONDAY, start_slot=18, duration_slots=2
    )
    
    session2 = Session(
        subject_id="sub-1", faculty_id="fac-2", room_id="room-2",
        section_id="sec-1", day=DayOfWeek.MONDAY, start_slot=18, duration_slots=2
    )
    
    violations = validate_session_constraints(session2, rooms_map, faculty_map, subjects_map, sections_map, [session1])
    assert any(v.type == "SECTION_CONFLICT" for v in violations)


def test_capacity_constraint():
    depts, rooms, faculty, subjects, sections = create_test_data()
    
    # Section has 25 students, room2 has capacity 30 - should work
    # But let's make room smaller
    small_room = Room(id="room-small", name="Small", building="Main", capacity=10, equipment=[Equipment.PROJECTOR], department_id="dept-1")
    rooms_map = {r.id: r for r in rooms + [small_room]}
    faculty_map = {f.id: f for f in faculty}
    subjects_map = {s.id: s for s in subjects}
    sections_map = {s.id: s for s in sections}
    
    session = Session(
        subject_id="sub-1", faculty_id="fac-1", room_id="room-small",
        section_id="sec-1", day=DayOfWeek.MONDAY, start_slot=18, duration_slots=2
    )
    
    violations = validate_session_constraints(session, rooms_map, faculty_map, subjects_map, sections_map, [])
    assert any(v.type == "CAPACITY_EXCEEDED" for v in violations)


def test_equipment_constraint():
    depts, rooms, faculty, subjects, sections = create_test_data()
    
    # Room without projector
    no_proj_room = Room(id="room-no-proj", name="No Proj", building="Main", capacity=50, equipment=[], department_id="dept-1")
    rooms_map = {r.id: r for r in rooms + [no_proj_room]}
    faculty_map = {f.id: f for f in faculty}
    subjects_map = {s.id: s for s in subjects}
    sections_map = {s.id: s for s in sections}
    
    session = Session(
        subject_id="sub-1", faculty_id="fac-1", room_id="room-no-proj",
        section_id="sec-1", day=DayOfWeek.MONDAY, start_slot=18, duration_slots=2
    )
    
    violations = validate_session_constraints(session, rooms_map, faculty_map, subjects_map, sections_map, [])
    assert any(v.type == "EQUIPMENT_MISSING" for v in violations)


def test_faculty_qualification_constraint():
    depts, rooms, faculty, subjects, sections = create_test_data()
    
    # Subject requires fac-1 or fac-2
    # Both faculty in test data have CS qualification, so let's create unqualified faculty
    unqualified = Faculty(
        id="fac-unq", name="Unqualified", email="uq@test.com",
        qualifications=["Math"], max_hours_per_week=20,
        availability=[Availability(day=DayOfWeek.MONDAY, start_time="09:00", end_time="17:00")],
        department_id="dept-1"
    )
    
    rooms_map = {r.id: r for r in rooms}
    faculty_map = {f.id: f for f in faculty + [unqualified]}
    subjects_map = {s.id: s for s in subjects}
    sections_map = {s.id: s for s in sections}
    
    session = Session(
        subject_id="sub-1", faculty_id="fac-unq", room_id="room-1",
        section_id="sec-1", day=DayOfWeek.MONDAY, start_slot=18, duration_slots=2
    )
    
    violations = validate_session_constraints(session, rooms_map, faculty_map, subjects_map, sections_map, [])
    assert any(v.type == "FACULTY_UNQUALIFIED" for v in violations)


def test_faculty_availability_constraint():
    depts, rooms, faculty, subjects, sections = create_test_data()
    
    rooms_map = {r.id: r for r in rooms}
    faculty_map = {f.id: f for f in faculty}
    subjects_map = {s.id: s for s in subjects}
    sections_map = {s.id: s for s in sections}
    
    # fac-1 only available Monday 09-17, try Tuesday
    session = Session(
        subject_id="sub-1", faculty_id="fac-1", room_id="room-1",
        section_id="sec-1", day=DayOfWeek.TUESDAY, start_slot=18, duration_slots=2
    )
    
    violations = validate_session_constraints(session, rooms_map, faculty_map, subjects_map, sections_map, [])
    assert any(v.type == "FACULTY_UNAVAILABLE" for v in violations)


def test_max_hours_constraint():
    depts, rooms, faculty, subjects, sections = create_test_data()
    
    rooms_map = {r.id: r for r in rooms}
    faculty_map = {f.id: f for f in faculty}
    subjects_map = {s.id: s for s in subjects}
    sections_map = {s.id: s for s in sections}
    
    # Create sessions that would exceed max_hours (20 hours = 40 slots)
    existing = [
        Session(subject_id="sub-1", faculty_id="fac-1", room_id="room-1", section_id="sec-1",
                day=DayOfWeek.MONDAY, start_slot=18, duration_slots=2)  # 1 hour
        for _ in range(20)  # 20 hours already
    ]
    
    session = Session(
        subject_id="sub-1", faculty_id="fac-1", room_id="room-2",
        section_id="sec-1", day=DayOfWeek.MONDAY, start_slot=20, duration_slots=2
    )
    
    violations = validate_session_constraints(session, rooms_map, faculty_map, subjects_map, sections_map, existing)
    assert any(v.type == "MAX_HOURS_EXCEEDED" for v in violations)


def test_unscheduled_sessions_reported():
    """Test that unscheduled sessions are reported when no valid slot exists."""
    dept = Department(id="dept-1", name="Test", code="TEST", college_id="col-1")
    
    # Room too small for section
    room = Room(id="room-1", name="Tiny", building="Main", capacity=5, equipment=[Equipment.PROJECTOR], department_id="dept-1")
    
    fac = Faculty(
        id="fac-1", name="Fac", email="f@test.com",
        qualifications=["CS"], max_hours_per_week=20,
        availability=[Availability(day=DayOfWeek.MONDAY, start_time="09:00", end_time="17:00")],
        department_id="dept-1"
    )
    
    sub = Subject(
        id="sub-1", code="CS101", name="CS",
        required_equipment=[Equipment.PROJECTOR], min_room_capacity=20,
        qualified_faculty_ids=["fac-1"], department_id="dept-1"
    )
    
    sec = Section(
        id="sec-1", name="Sec A", student_count=30, department_id="dept-1",
        subject_requirements=[SubjectRequirement(subject_id="sub-1", sessions_per_week=1, session_duration_minutes=60)]
    )
    
    timetable = generate_timetable([dept], [room], [fac], [sub], [sec])
    
    assert len(timetable.sessions) == 0
    assert len(timetable.unscheduled) == 1
    assert timetable.unscheduled[0].required_sessions == 1
    assert timetable.unscheduled[0].scheduled_sessions == 0
    # The scheduler reports NO_ELIGIBLE_RESOURCES when no room meets capacity/equipment requirements
    assert any(v.type == "NO_ELIGIBLE_RESOURCES" for v in timetable.unscheduled[0].violations)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])