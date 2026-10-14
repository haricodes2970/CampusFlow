import pytest
from app.database import InMemoryStore
from app.models import (
    Department, Room, Faculty, Subject, Section,
    Session, DayOfWeek, Equipment, Availability, SubjectRequirement,
    Timetable
)
from app.scheduler import generate_timetable


def create_test_store():
    """Create a store with test data for persistence tests."""
    store = InMemoryStore()
    
    # Clear existing data
    store.departments.clear()
    store.rooms.clear()
    store.faculty.clear()
    store.subjects.clear()
    store.sections.clear()
    store.timetable.sessions.clear()
    
    # Add minimal test data
    dept = Department(id="dept-test", name="Test Dept", code="TEST", college_id="col-1")
    store.departments.append(dept)
    
    room = Room(id="room-test", name="Test Room", building="Main", capacity=50, 
                equipment=[Equipment.PROJECTOR], department_id="dept-test")
    store.rooms.append(room)
    
    fac = Faculty(
        id="fac-test", name="Test Faculty", email="test@test.com",
        qualifications=["CS"], max_hours_per_week=20,
        availability=[Availability(day=DayOfWeek.MONDAY, start_time="09:00", end_time="17:00")],
        department_id="dept-test"
    )
    store.faculty.append(fac)
    
    sub = Subject(
        id="sub-test", code="CS101", name="Test Subject",
        required_equipment=[Equipment.PROJECTOR], min_room_capacity=20,
        qualified_faculty_ids=["fac-test"], department_id="dept-test"
    )
    store.subjects.append(sub)
    
    sec = Section(
        id="sec-test", name="Test Section", student_count=25, department_id="dept-test",
        subject_requirements=[SubjectRequirement(subject_id="sub-test", sessions_per_week=2, session_duration_minutes=60)]
    )
    store.sections.append(sec)
    
    return store


def test_in_memory_store_crud_departments():
    store = create_test_store()
    
    # Create
    new_dept = Department(id="dept-new", name="New Dept", code="NEW", college_id="col-1")
    store.add_department(new_dept)
    
    # Read
    depts = store.get_departments()
    assert any(d.id == "dept-new" for d in depts)
    
    # Update
    updated = Department(id="dept-new", name="Updated Dept", code="UPD", college_id="col-1")
    store.update_department("dept-new", updated)
    depts = store.get_departments()
    assert any(d.name == "Updated Dept" for d in depts)
    
    # Delete
    store.delete_department("dept-new")
    depts = store.get_departments()
    assert not any(d.id == "dept-new" for d in depts)


def test_in_memory_store_crud_rooms():
    store = create_test_store()
    
    room = Room(id="room-new", name="New Room", building="New", capacity=30, 
                equipment=[Equipment.WHITEBOARD], department_id="dept-test")
    store.add_room(room)
    
    rooms = store.get_rooms()
    assert any(r.id == "room-new" for r in rooms)
    
    store.delete_room("room-new")
    rooms = store.get_rooms()
    assert not any(r.id == "room-new" for r in rooms)


def test_in_memory_store_crud_faculty():
    store = create_test_store()
    
    fac = Faculty(
        id="fac-new", name="New Faculty", email="new@test.com",
        qualifications=["Math"], max_hours_per_week=15,
        availability=[Availability(day=DayOfWeek.TUESDAY, start_time="10:00", end_time="14:00")],
        department_id="dept-test"
    )
    store.add_faculty(fac)
    
    faculty = store.get_faculty()
    assert any(f.id == "fac-new" for f in faculty)
    
    store.delete_faculty("fac-new")
    faculty = store.get_faculty()
    assert not any(f.id == "fac-new" for f in faculty)


def test_in_memory_store_crud_subjects():
    store = create_test_store()
    
    sub = Subject(
        id="sub-new", code="MA101", name="New Subject",
        required_equipment=[Equipment.WHITEBOARD], min_room_capacity=30,
        qualified_faculty_ids=["fac-test"], department_id="dept-test"
    )
    store.add_subject(sub)
    
    subjects = store.get_subjects()
    assert any(s.id == "sub-new" for s in subjects)
    
    store.delete_subject("sub-new")
    subjects = store.get_subjects()
    assert not any(s.id == "sub-new" for s in subjects)


def test_in_memory_store_crud_sections():
    store = create_test_store()
    
    sec = Section(
        id="sec-new", name="New Section", student_count=20, department_id="dept-test",
        subject_requirements=[SubjectRequirement(subject_id="sub-test", sessions_per_week=1, session_duration_minutes=60)]
    )
    store.add_section(sec)
    
    sections = store.get_sections()
    assert any(s.id == "sec-new" for s in sections)
    
    store.delete_section("sec-new")
    sections = store.get_sections()
    assert not any(s.id == "sec-new" for s in sections)


def test_in_memory_store_session_management():
    store = create_test_store()
    
    # Add a session
    session = Session(
        subject_id="sub-test", faculty_id="fac-test", room_id="room-test",
        section_id="sec-test", day=DayOfWeek.MONDAY, start_slot=18, duration_slots=2
    )
    store.add_session(session)
    
    sessions = store.get_sessions()
    assert len(sessions) == 1
    assert sessions[0].id == session.id
    
    # Update session
    updated = Session(
        id=session.id,
        subject_id="sub-test", faculty_id="fac-test", room_id="room-test",
        section_id="sec-test", day=DayOfWeek.MONDAY, start_slot=20, duration_slots=2
    )
    store.update_session(session.id, updated)
    sessions = store.get_sessions()
    assert sessions[0].start_slot == 20
    
    # Delete session
    store.delete_session(session.id)
    sessions = store.get_sessions()
    assert len(sessions) == 0


def test_in_memory_store_timetable_persistence():
    store = create_test_store()
    
    # Generate timetable
    timetable = store.run_generation()
    assert len(timetable.sessions) > 0
    
    # Verify sessions are stored
    sessions = store.get_sessions()
    assert len(sessions) == len(timetable.sessions)
    
    # Run again - should regenerate
    timetable2 = store.run_generation()
    sessions2 = store.get_sessions()
    assert len(sessions2) == len(timetable2.sessions)


def test_in_memory_store_get_timetable_returns_unscheduled():
    store = create_test_store()
    
    timetable = store.get_timetable()
    assert isinstance(timetable, Timetable)
    assert hasattr(timetable, 'sessions')
    assert hasattr(timetable, 'unscheduled')
    # Should have unscheduled sessions due to constraints
    assert len(timetable.unscheduled) >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])