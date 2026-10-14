from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum
from datetime import time
import uuid


class DayOfWeek(str, Enum):
    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"
    SUNDAY = "SUNDAY"


class Availability(BaseModel):
    day: DayOfWeek
    start_time: str  # HH:MM format
    end_time: str    # HH:MM format


class Equipment(str, Enum):
    PROJECTOR = "PROJECTOR"
    WHITEBOARD = "WHITEBOARD"
    COMPUTERS = "COMPUTERS"
    AUDIO_SYSTEM = "AUDIO_SYSTEM"
    VIDEO_CONFERENCE = "VIDEO_CONFERENCE"
    SMART_BOARD = "SMART_BOARD"


class Department(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    code: str
    college_id: str


class Room(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    building: str
    capacity: int
    equipment: List[Equipment] = []
    department_id: str


class Faculty(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: str
    qualifications: List[str] = []
    max_hours_per_week: int = 20
    availability: List[Availability] = []
    department_id: str


class Subject(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    code: str
    name: str
    required_equipment: List[Equipment] = []
    min_room_capacity: int = 0
    qualified_faculty_ids: List[str] = []
    department_id: str


class Section(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    student_count: int
    department_id: str
    subject_requirements: List["SubjectRequirement"] = []


class SubjectRequirement(BaseModel):
    subject_id: str
    sessions_per_week: int
    session_duration_minutes: int = 60


class Session(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    subject_id: str
    faculty_id: str
    room_id: str
    section_id: str
    day: DayOfWeek
    start_slot: int  # 0-based slot index (each slot = 30 min)
    duration_slots: int  # number of 30-min slots


class ConstraintViolation(BaseModel):
    type: str
    message: str
    entity_id: str
    entity_type: str


class UnscheduledSession(BaseModel):
    subject_id: str
    section_id: str
    subject_name: str
    section_name: str
    required_sessions: int
    scheduled_sessions: int
    violations: List[ConstraintViolation]


class Timetable(BaseModel):
    sessions: List[Session] = []
    unscheduled: List[UnscheduledSession] = []


# Update forward reference
Section.model_rebuild()