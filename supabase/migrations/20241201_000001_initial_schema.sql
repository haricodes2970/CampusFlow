-- CampusFlow Initial Schema Migration
-- Creates all core tables with constraints, indexes, and RLS policies

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Colleges table (top-level entity)
CREATE TABLE colleges (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    code TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Departments table
CREATE TABLE departments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    code TEXT NOT NULL,
    college_id UUID NOT NULL REFERENCES colleges(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(college_id, code)
);

-- Rooms table
CREATE TABLE rooms (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    building TEXT NOT NULL,
    capacity INT NOT NULL CHECK (capacity > 0),
    equipment TEXT[] NOT NULL DEFAULT '{}', -- Equipment enum values
    department_id UUID REFERENCES departments(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Faculty table
CREATE TABLE faculty (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    qualifications TEXT[] NOT NULL DEFAULT '{}',
    max_hours_per_week INT NOT NULL DEFAULT 20 CHECK (max_hours_per_week >= 0),
    department_id UUID REFERENCES departments(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Faculty availability table (normalized)
CREATE TABLE faculty_availability (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    faculty_id UUID NOT NULL REFERENCES faculty(id) ON DELETE CASCADE,
    day_of_week TEXT NOT NULL CHECK (day_of_week IN ('MONDAY','TUESDAY','WEDNESDAY','THURSDAY','FRIDAY','SATURDAY','SUNDAY')),
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(faculty_id, day_of_week, start_time, end_time)
);

-- Subjects table
CREATE TABLE subjects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code TEXT NOT NULL,
    name TEXT NOT NULL,
    required_equipment TEXT[] NOT NULL DEFAULT '{}', -- Equipment enum values
    min_room_capacity INT NOT NULL DEFAULT 0 CHECK (min_room_capacity >= 0),
    qualified_faculty_ids UUID[] NOT NULL DEFAULT '{}',
    department_id UUID REFERENCES departments(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(department_id, code)
);

-- Sections (student cohorts) table
CREATE TABLE sections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    student_count INT NOT NULL CHECK (student_count > 0),
    department_id UUID REFERENCES departments(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Section subject requirements (normalized many-to-many)
CREATE TABLE section_subject_requirements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    section_id UUID NOT NULL REFERENCES sections(id) ON DELETE CASCADE,
    subject_id UUID NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
    sessions_per_week INT NOT NULL CHECK (sessions_per_week > 0),
    session_duration_minutes INT NOT NULL DEFAULT 60 CHECK (session_duration_minutes > 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(section_id, subject_id)
);

-- Timetable sessions table
CREATE TABLE timetable_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    subject_id UUID NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
    faculty_id UUID NOT NULL REFERENCES faculty(id) ON DELETE CASCADE,
    room_id UUID NOT NULL REFERENCES rooms(id) ON DELETE CASCADE,
    section_id UUID NOT NULL REFERENCES sections(id) ON DELETE CASCADE,
    day_of_week TEXT NOT NULL CHECK (day_of_week IN ('MONDAY','TUESDAY','WEDNESDAY','THURSDAY','FRIDAY','SATURDAY','SUNDAY')),
    start_slot INT NOT NULL CHECK (start_slot >= 0 AND start_slot < 48), -- 30-min slots in 24h
    duration_slots INT NOT NULL CHECK (duration_slots > 0 AND duration_slots <= 48),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for common query patterns
CREATE INDEX idx_rooms_department ON rooms(department_id);
CREATE INDEX idx_rooms_capacity ON rooms(capacity);
CREATE INDEX idx_faculty_department ON faculty(department_id);
CREATE INDEX idx_faculty_availability_faculty ON faculty_availability(faculty_id);
CREATE INDEX idx_subjects_department ON subjects(department_id);
CREATE INDEX idx_subjects_qualified_faculty ON subjects USING GIN(qualified_faculty_ids);
CREATE INDEX idx_sections_department ON sections(department_id);
CREATE INDEX idx_section_requirements_section ON section_subject_requirements(section_id);
CREATE INDEX idx_section_requirements_subject ON section_subject_requirements(subject_id);
CREATE INDEX idx_timetable_sessions_section_day ON timetable_sessions(section_id, day_of_week);
CREATE INDEX idx_timetable_sessions_faculty_day ON timetable_sessions(faculty_id, day_of_week);
CREATE INDEX idx_timetable_sessions_room_day ON timetable_sessions(room_id, day_of_week);
CREATE INDEX idx_timetable_sessions_subject ON timetable_sessions(subject_id);

-- Updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at triggers
CREATE TRIGGER update_colleges_updated_at BEFORE UPDATE ON colleges FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_departments_updated_at BEFORE UPDATE ON departments FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_rooms_updated_at BEFORE UPDATE ON rooms FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_faculty_updated_at BEFORE UPDATE ON faculty FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_subjects_updated_at BEFORE UPDATE ON subjects FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_sections_updated_at BEFORE UPDATE ON sections FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_timetable_sessions_updated_at BEFORE UPDATE ON timetable_sessions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Row Level Security (RLS) - Enable on all tables
ALTER TABLE colleges ENABLE ROW LEVEL SECURITY;
ALTER TABLE departments ENABLE ROW LEVEL SECURITY;
ALTER TABLE rooms ENABLE ROW LEVEL SECURITY;
ALTER TABLE faculty ENABLE ROW LEVEL SECURITY;
ALTER TABLE faculty_availability ENABLE ROW LEVEL SECURITY;
ALTER TABLE subjects ENABLE ROW LEVEL SECURITY;
ALTER TABLE sections ENABLE ROW LEVEL SECURITY;
ALTER TABLE section_subject_requirements ENABLE ROW LEVEL SECURITY;
ALTER TABLE timetable_sessions ENABLE ROW LEVEL SECURITY;

-- RLS Policies: For demo/development, allow all operations for authenticated users
-- In production, these should be restricted based on authentication/authorization
CREATE POLICY "Allow all for authenticated users" ON colleges FOR ALL TO authenticated USING (true) WITH CHECK (true);
CREATE POLICY "Allow all for authenticated users" ON departments FOR ALL TO authenticated USING (true) WITH CHECK (true);
CREATE POLICY "Allow all for authenticated users" ON rooms FOR ALL TO authenticated USING (true) WITH CHECK (true);
CREATE POLICY "Allow all for authenticated users" ON faculty FOR ALL TO authenticated USING (true) WITH CHECK (true);
CREATE POLICY "Allow all for authenticated users" ON faculty_availability FOR ALL TO authenticated USING (true) WITH CHECK (true);
CREATE POLICY "Allow all for authenticated users" ON subjects FOR ALL TO authenticated USING (true) WITH CHECK (true);
CREATE POLICY "Allow all for authenticated users" ON sections FOR ALL TO authenticated USING (true) WITH CHECK (true);
CREATE POLICY "Allow all for authenticated users" ON section_subject_requirements FOR ALL TO authenticated USING (true) WITH CHECK (true);
CREATE POLICY "Allow all for authenticated users" ON timetable_sessions FOR ALL TO authenticated USING (true) WITH CHECK (true);

-- Also allow anon key for demo purposes (read-only for most, write for sessions)
CREATE POLICY "Allow anon read" ON colleges FOR SELECT TO anon USING (true);
CREATE POLICY "Allow anon read" ON departments FOR SELECT TO anon USING (true);
CREATE POLICY "Allow anon read" ON rooms FOR SELECT TO anon USING (true);
CREATE POLICY "Allow anon read" ON faculty FOR SELECT TO anon USING (true);
CREATE POLICY "Allow anon read" ON faculty_availability FOR SELECT TO anon USING (true);
CREATE POLICY "Allow anon read" ON subjects FOR SELECT TO anon USING (true);
CREATE POLICY "Allow anon read" ON sections FOR SELECT TO anon USING (true);
CREATE POLICY "Allow anon read" ON section_subject_requirements FOR SELECT TO anon USING (true);
CREATE POLICY "Allow anon read" ON timetable_sessions FOR SELECT TO anon USING (true);
CREATE POLICY "Allow anon write sessions" ON timetable_sessions FOR INSERT, UPDATE, DELETE TO anon USING (true) WITH CHECK (true);