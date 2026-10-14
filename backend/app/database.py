from typing import List
from .models import (
    Department, Room, Faculty, Subject, Section, Session,
    Timetable, DayOfWeek, Equipment, Availability, SubjectRequirement
)
from .scheduler import generate_timetable
import os

class InMemoryStore:
    """Local in-memory fallback store for development/demo without Supabase."""
    
    def __init__(self):
        self.departments: List[Department] = []
        self.rooms: List[Room] = []
        self.faculty: List[Faculty] = []
        self.subjects: List[Subject] = []
        self.sections: List[Section] = []
        self.timetable: Timetable = Timetable(sessions=[], unscheduled=[])
        self.load_seed_data()

    def load_seed_data(self):
        """Load rich demo data for testing."""
        cs = Department(id="dept-cs", name="Computer Science & Eng", code="CSE", college_id="college-main")
        ee = Department(id="dept-ee", name="Electrical Engineering", code="EE", college_id="college-main")
        ma = Department(id="dept-ma", name="Mathematics", code="MATH", college_id="college-main")
        self.departments = [cs, ee, ma]

        self.rooms = [
            Room(id="room-101", name="Lab 101", building="Science Block", capacity=60, 
                 equipment=[Equipment.PROJECTOR, Equipment.COMPUTERS, Equipment.WHITEBOARD], department_id="dept-cs"),
            Room(id="room-102", name="Lecture Hall A", building="Science Block", capacity=120, 
                 equipment=[Equipment.PROJECTOR, Equipment.AUDIO_SYSTEM, Equipment.WHITEBOARD], department_id="dept-cs"),
            Room(id="room-201", name="EE Lab 201", building="Engineering Hall", capacity=45, 
                 equipment=[Equipment.PROJECTOR, Equipment.COMPUTERS], department_id="dept-ee"),
            Room(id="room-301", name="Math Hall 301", building="Arts Building", capacity=90, 
                 equipment=[Equipment.WHITEBOARD, Equipment.SMART_BOARD], department_id="dept-ma"),
        ]

        self.faculty = [
            Faculty(
                id="fac-1", name="Dr. Alan Turing", email="turing@campusflow.edu",
                qualifications=["Algorithms", "Data Structures", "AI"], max_hours_per_week=18,
                availability=[
                    Availability(day=DayOfWeek.MONDAY, start_time="09:00", end_time="17:00"),
                    Availability(day=DayOfWeek.WEDNESDAY, start_time="09:00", end_time="17:00"),
                    Availability(day=DayOfWeek.FRIDAY, start_time="09:00", end_time="17:00"),
                ], department_id="dept-cs"
            ),
            Faculty(
                id="fac-2", name="Prof. Grace Hopper", email="hopper@campusflow.edu",
                qualifications=["Operating Systems", "Compilers", "Data Structures"], max_hours_per_week=20,
                availability=[
                    Availability(day=DayOfWeek.TUESDAY, start_time="08:00", end_time="16:00"),
                    Availability(day=DayOfWeek.THURSDAY, start_time="08:00", end_time="16:00"),
                ], department_id="dept-cs"
            ),
            Faculty(
                id="fac-3", name="Dr. Nikola Tesla", email="tesla@campusflow.edu",
                qualifications=["Circuit Analysis", "Electromagnetism"], max_hours_per_week=16,
                availability=[
                    Availability(day=DayOfWeek.MONDAY, start_time="10:00", end_time="15:00"),
                    Availability(day=DayOfWeek.WEDNESDAY, start_time="10:00", end_time="15:00"),
                ], department_id="dept-ee"
            ),
            Faculty(
                id="fac-4", name="Dr. Katherine Johnson", email="johnson@campusflow.edu",
                qualifications=["Linear Algebra", "Calculus", "Differential Equations"], max_hours_per_week=20,
                availability=[
                    Availability(day=DayOfWeek.MONDAY, start_time="09:00", end_time="17:00"),
                    Availability(day=DayOfWeek.TUESDAY, start_time="09:00", end_time="17:00"),
                    Availability(day=DayOfWeek.WEDNESDAY, start_time="09:00", end_time="17:00"),
                    Availability(day=DayOfWeek.THURSDAY, start_time="09:00", end_time="17:00"),
                    Availability(day=DayOfWeek.FRIDAY, start_time="09:00", end_time="17:00"),
                ], department_id="dept-ma"
            ),
        ]

        self.subjects = [
            Subject(
                id="sub-ds", code="CS201", name="Data Structures & Algorithms",
                required_equipment=[Equipment.PROJECTOR, Equipment.COMPUTERS], min_room_capacity=50,
                qualified_faculty_ids=["fac-1", "fac-2"], department_id="dept-cs"
            ),
            Subject(
                id="sub-os", code="CS301", name="Operating Systems",
                required_equipment=[Equipment.PROJECTOR, Equipment.WHITEBOARD], min_room_capacity=100,
                qualified_faculty_ids=["fac-2"], department_id="dept-cs"
            ),
            Subject(
                id="sub-ee", code="EE101", name="Circuit Analysis",
                required_equipment=[Equipment.PROJECTOR, Equipment.COMPUTERS], min_room_capacity=40,
                qualified_faculty_ids=["fac-3"], department_id="dept-ee"
            ),
            Subject(
                id="sub-calc", code="MA101", name="Linear Algebra & Calculus",
                required_equipment=[Equipment.WHITEBOARD], min_room_capacity=80,
                qualified_faculty_ids=["fac-4"], department_id="dept-ma"
            ),
        ]

        self.sections = [
            Section(
                id="sec-cs-3a", name="CSE 3rd Year A", student_count=55, department_id="dept-cs",
                subject_requirements=[
                    SubjectRequirement(subject_id="sub-ds", sessions_per_week=3, session_duration_minutes=60),
                    SubjectRequirement(subject_id="sub-os", sessions_per_week=2, session_duration_minutes=90),
                    SubjectRequirement(subject_id="sub-calc", sessions_per_week=2, session_duration_minutes=60),
                ]
            ),
            Section(
                id="sec-ee-2a", name="EE 2nd Year A", student_count=40, department_id="dept-ee",
                subject_requirements=[
                    SubjectRequirement(subject_id="sub-ee", sessions_per_week=3, session_duration_minutes=90),
                    SubjectRequirement(subject_id="sub-calc", sessions_per_week=2, session_duration_minutes=60),
                ]
            ),
        ]

        self.run_generation()

    def run_generation(self) -> Timetable:
        self.timetable = generate_timetable(
            self.departments, self.rooms, self.faculty, self.subjects, self.sections
        )
        return self.timetable

    # CRUD methods
    def get_departments(self) -> List[Department]:
        return self.departments

    def add_department(self, dept: Department) -> Department:
        self.departments.append(dept)
        return dept

    def update_department(self, dept_id: str, dept: Department) -> Department:
        idx = next((i for i, d in enumerate(self.departments) if d.id == dept_id), None)
        if idx is None:
            raise ValueError("Department not found")
        self.departments[idx] = dept
        return dept

    def delete_department(self, dept_id: str):
        self.departments = [d for d in self.departments if d.id != dept_id]

    def get_rooms(self) -> List[Room]:
        return self.rooms

    def add_room(self, room: Room) -> Room:
        self.rooms.append(room)
        return room

    def update_room(self, room_id: str, room: Room) -> Room:
        idx = next((i for i, r in enumerate(self.rooms) if r.id == room_id), None)
        if idx is None:
            raise ValueError("Room not found")
        self.rooms[idx] = room
        return room

    def delete_room(self, room_id: str):
        self.rooms = [r for r in self.rooms if r.id != room_id]

    def get_faculty(self) -> List[Faculty]:
        return self.faculty

    def add_faculty(self, fac: Faculty) -> Faculty:
        self.faculty.append(fac)
        return fac

    def update_faculty(self, faculty_id: str, fac: Faculty) -> Faculty:
        idx = next((i for i, f in enumerate(self.faculty) if f.id == faculty_id), None)
        if idx is None:
            raise ValueError("Faculty not found")
        self.faculty[idx] = fac
        return fac

    def delete_faculty(self, faculty_id: str):
        self.faculty = [f for f in self.faculty if f.id != faculty_id]

    def get_subjects(self) -> List[Subject]:
        return self.subjects

    def add_subject(self, sub: Subject) -> Subject:
        self.subjects.append(sub)
        return sub

    def update_subject(self, subject_id: str, sub: Subject) -> Subject:
        idx = next((i for i, s in enumerate(self.subjects) if s.id == subject_id), None)
        if idx is None:
            raise ValueError("Subject not found")
        self.subjects[idx] = sub
        return sub

    def delete_subject(self, subject_id: str):
        self.subjects = [s for s in self.subjects if s.id != subject_id]

    def get_sections(self) -> List[Section]:
        return self.sections

    def add_section(self, sec: Section) -> Section:
        self.sections.append(sec)
        return sec

    def update_section(self, section_id: str, sec: Section) -> Section:
        idx = next((i for i, s in enumerate(self.sections) if s.id == section_id), None)
        if idx is None:
            raise ValueError("Section not found")
        self.sections[idx] = sec
        return sec

    def delete_section(self, section_id: str):
        self.sections = [s for s in self.sections if s.id != section_id]

    def get_sessions(self) -> List[Session]:
        return self.timetable.sessions

    def add_session(self, session: Session) -> Session:
        self.timetable.sessions.append(session)
        return session

    def update_session(self, session_id: str, session: Session) -> Session:
        idx = next((i for i, s in enumerate(self.timetable.sessions) if s.id == session_id), None)
        if idx is None:
            raise ValueError("Session not found")
        self.timetable.sessions[idx] = session
        return session

    def delete_session(self, session_id: str):
        self.timetable.sessions = [s for s in self.timetable.sessions if s.id != session_id]

    def clear_sessions(self):
        self.timetable.sessions = []

    def get_timetable(self) -> Timetable:
        return self.timetable


def get_store():
    """
    Factory function that returns the appropriate store based on configuration.
    Uses Supabase if SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are set,
    otherwise falls back to in-memory store.
    """
    supabase_url = os.getenv("SUPABASE_URL", "").strip()
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    
    if supabase_url and supabase_key:
        try:
            from .supabase_store import SupabaseStore
            return SupabaseStore(supabase_url, supabase_key)
        except Exception as e:
            print(f"Warning: Failed to initialize Supabase store: {e}. Falling back to in-memory store.")
    
    return InMemoryStore()


# Singleton instance
store = get_store()