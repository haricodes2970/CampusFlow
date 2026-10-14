from typing import List, Dict, Optional
import os
from .models import (
    Department, Room, Faculty, Subject, Section, Session,
    Timetable, DayOfWeek, Equipment, Availability, SubjectRequirement
)
from .scheduler import generate_timetable, validate_session_constraints, calculate_preference_score

# In-memory storage for MVP / local demo mode
class InMemoryStore:
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
        # Departments
        cs = Department(id="dept-cs", name="Computer Science & Eng", code="CSE", college_id="college-main")
        ee = Department(id="dept-ee", name="Electrical Engineering", code="EE", college_id="college-main")
        ma = Department(id="dept-ma", name="Mathematics", code="MATH", college_id="college-main")
        self.departments = [cs, ee, ma]

        # Rooms
        self.rooms = [
            Room(id="room-101", name="Lab 101", building="Science Block", capacity=60, equipment=[Equipment.PROJECTOR, Equipment.COMPUTERS, Equipment.WHITEBOARD], department_id="dept-cs"),
            Room(id="room-102", name="Lecture Hall A", building="Science Block", capacity=120, equipment=[Equipment.PROJECTOR, Equipment.AUDIO_SYSTEM, Equipment.WHITEBOARD], department_id="dept-cs"),
            Room(id="room-201", name="EE Lab 201", building="Engineering Hall", capacity=45, equipment=[Equipment.PROJECTOR, Equipment.COMPUTERS], department_id="dept-ee"),
            Room(id="room-301", name="Math Hall 301", building="Arts Building", capacity=90, equipment=[Equipment.WHITEBOARD, Equipment.SMART_BOARD], department_id="dept-ma"),
        ]

        # Faculty
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

        # Subjects
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

        # Sections
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

        # Run initial generation
        self.run_generation()

    def run_generation(self):
        self.timetable = generate_timetable(
            self.departments, self.rooms, self.faculty, self.subjects, self.sections
        )


store = InMemoryStore()