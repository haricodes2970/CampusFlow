export type DayOfWeek = 'MONDAY' | 'TUESDAY' | 'WEDNESDAY' | 'THURSDAY' | 'FRIDAY' | 'SATURDAY' | 'SUNDAY';

export type Equipment = 'PROJECTOR' | 'WHITEBOARD' | 'COMPUTERS' | 'AUDIO_SYSTEM' | 'VIDEO_CONFERENCE' | 'SMART_BOARD';

export interface Availability {
  day: DayOfWeek;
  start_time: string;
  end_time: string;
}

export interface Department {
  id: string;
  name: string;
  code: string;
  college_id: string;
}

export interface Room {
  id: string;
  name: string;
  building: string;
  capacity: number;
  equipment: Equipment[];
  department_id: string;
}

export interface Faculty {
  id: string;
  name: string;
  email: string;
  qualifications: string[];
  max_hours_per_week: number;
  availability: Availability[];
  department_id: string;
}

export interface Subject {
  id: string;
  code: string;
  name: string;
  required_equipment: Equipment[];
  min_room_capacity: number;
  qualified_faculty_ids: string[];
  department_id: string;
}

export interface SubjectRequirement {
  subject_id: string;
  sessions_per_week: number;
  session_duration_minutes: number;
}

export interface Section {
  id: string;
  name: string;
  student_count: number;
  department_id: string;
  subject_requirements: SubjectRequirement[];
}

export interface Session {
  id: string;
  subject_id: string;
  faculty_id: string;
  room_id: string;
  section_id: string;
  day: DayOfWeek;
  start_slot: number;
  duration_slots: number;
}

export interface ConstraintViolation {
  type: string;
  message: string;
  entity_id: string;
  entity_type: string;
}

export interface UnscheduledSession {
  subject_id: string;
  section_id: string;
  subject_name: string;
  section_name: string;
  required_sessions: number;
  scheduled_sessions: number;
  violations: ConstraintViolation[];
}

export interface Timetable {
  sessions: Session[];
  unscheduled: UnscheduledSession[];
}

export interface Stats {
  departments: number;
  rooms: number;
  faculty: number;
  subjects: number;
  sections: number;
  scheduled_sessions: number;
  unscheduled_sessions: number;
  unscheduled_details: number;
}
