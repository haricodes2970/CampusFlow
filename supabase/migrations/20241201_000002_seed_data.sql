-- CampusFlow Seed Data Migration
-- Inserts realistic demo data for development and demonstration
-- Uses ON CONFLICT to be idempotent (safe to run multiple times)

-- Insert college
INSERT INTO colleges (id, name, code) VALUES
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'Main Campus University', 'MAIN')
ON CONFLICT (code) DO NOTHING;

-- Insert departments
INSERT INTO departments (id, name, code, college_id) VALUES
    ('dept-cs-dept-cs-dept-cs-deptcsdept', 'Computer Science & Engineering', 'CSE', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'),
    ('dept-ee-dept-ee-dept-ee-depteedept', 'Electrical Engineering', 'EE', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'),
    ('dept-ma-dept-ma-dept-ma-deptmadept', 'Mathematics', 'MATH', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa')
ON CONFLICT (college_id, code) DO NOTHING;

-- Insert rooms
INSERT INTO rooms (id, name, building, capacity, equipment, department_id) VALUES
    ('room-101-room-101-room-101-room101', 'Lab 101', 'Science Block', 60, ARRAY['PROJECTOR','COMPUTERS','WHITEBOARD'], 'dept-cs-dept-cs-dept-cs-deptcsdept'),
    ('room-102-room-102-room-102-room102', 'Lecture Hall A', 'Science Block', 120, ARRAY['PROJECTOR','AUDIO_SYSTEM','WHITEBOARD'], 'dept-cs-dept-cs-dept-cs-deptcsdept'),
    ('room-201-room-201-room-201-room201', 'EE Lab 201', 'Engineering Hall', 45, ARRAY['PROJECTOR','COMPUTERS'], 'dept-ee-dept-ee-dept-ee-depteedept'),
    ('room-301-room-301-room-301-room301', 'Math Hall 301', 'Arts Building', 90, ARRAY['WHITEBOARD','SMART_BOARD'], 'dept-ma-dept-ma-dept-ma-deptmadept')
ON CONFLICT (id) DO NOTHING;

-- Insert faculty
INSERT INTO faculty (id, name, email, qualifications, max_hours_per_week, department_id) VALUES
    ('fac-00000001-fac1-fac1-fac00000001', 'Dr. Alan Turing', 'turing@campusflow.edu', ARRAY['Algorithms','Data Structures','AI'], 18, 'dept-cs-dept-cs-dept-cs-deptcsdept'),
    ('fac-00000002-fac2-fac2-fac00000002', 'Prof. Grace Hopper', 'hopper@campusflow.edu', ARRAY['Operating Systems','Compilers','Data Structures'], 20, 'dept-cs-dept-cs-dept-cs-deptcsdept'),
    ('fac-00000003-fac3-fac3-fac00000003', 'Dr. Nikola Tesla', 'tesla@campusflow.edu', ARRAY['Circuit Analysis','Electromagnetism'], 16, 'dept-ee-dept-ee-dept-ee-depteedept'),
    ('fac-00000004-fac4-fac4-fac00000004', 'Dr. Katherine Johnson', 'johnson@campusflow.edu', ARRAY['Linear Algebra','Calculus','Differential Equations'], 20, 'dept-ma-dept-ma-dept-ma-deptmadept')
ON CONFLICT (email) DO NOTHING;

-- Insert faculty availability
INSERT INTO faculty_availability (faculty_id, day_of_week, start_time, end_time) VALUES
    -- Dr. Alan Turing: Mon/Wed/Fri 9am-5pm
    ('fac-00000001-fac1-fac1-fac00000001', 'MONDAY', '09:00', '17:00'),
    ('fac-00000001-fac1-fac1-fac00000001', 'WEDNESDAY', '09:00', '17:00'),
    ('fac-00000001-fac1-fac1-fac00000001', 'FRIDAY', '09:00', '17:00'),
    -- Prof. Grace Hopper: Tue/Thu 8am-4pm
    ('fac-00000002-fac2-fac2-fac00000002', 'TUESDAY', '08:00', '16:00'),
    ('fac-00000002-fac2-fac2-fac00000002', 'THURSDAY', '08:00', '16:00'),
    -- Dr. Nikola Tesla: Mon/Wed 10am-3pm
    ('fac-00000003-fac3-fac3-fac00000003', 'MONDAY', '10:00', '15:00'),
    ('fac-00000003-fac3-fac3-fac00000003', 'WEDNESDAY', '10:00', '15:00'),
    -- Dr. Katherine Johnson: Mon-Fri 9am-5pm
    ('fac-00000004-fac4-fac4-fac00000004', 'MONDAY', '09:00', '17:00'),
    ('fac-00000004-fac4-fac4-fac00000004', 'TUESDAY', '09:00', '17:00'),
    ('fac-00000004-fac4-fac4-fac00000004', 'WEDNESDAY', '09:00', '17:00'),
    ('fac-00000004-fac4-fac4-fac00000004', 'THURSDAY', '09:00', '17:00'),
    ('fac-00000004-fac4-fac4-fac00000004', 'FRIDAY', '09:00', '17:00')
ON CONFLICT (faculty_id, day_of_week, start_time, end_time) DO NOTHING;

-- Insert subjects
INSERT INTO subjects (id, code, name, required_equipment, min_room_capacity, qualified_faculty_ids, department_id) VALUES
    ('sub-ds-sub-ds-sub-ds-subdsdsdsds', 'CS201', 'Data Structures & Algorithms', ARRAY['PROJECTOR','COMPUTERS'], 50, ARRAY['fac-00000001-fac1-fac1-fac00000001','fac-00000002-fac2-fac2-fac00000002'], 'dept-cs-dept-cs-dept-cs-deptcsdept'),
    ('sub-os-sub-os-sub-os-subososos', 'CS301', 'Operating Systems', ARRAY['PROJECTOR','WHITEBOARD'], 100, ARRAY['fac-00000002-fac2-fac2-fac00000002'], 'dept-cs-dept-cs-dept-cs-deptcsdept'),
    ('sub-ee-sub-ee-sub-ee-subeesubs', 'EE101', 'Circuit Analysis', ARRAY['PROJECTOR','COMPUTERS'], 40, ARRAY['fac-00000003-fac3-fac3-fac00000003'], 'dept-ee-dept-ee-dept-ee-depteedept'),
    ('sub-ca-sub-ca-sub-ca-subcacaca', 'MA101', 'Linear Algebra & Calculus', ARRAY['WHITEBOARD'], 80, ARRAY['fac-00000004-fac4-fac4-fac00000004'], 'dept-ma-dept-ma-dept-ma-deptmadept')
ON CONFLICT (department_id, code) DO NOTHING;

-- Insert sections
INSERT INTO sections (id, name, student_count, department_id) VALUES
    ('sec-cs3a-sec-cs3a-sec-cs3a-sec3a', 'CSE 3rd Year A', 55, 'dept-cs-dept-cs-dept-cs-deptcsdept'),
    ('sec-ee2a-sec-ee2a-sec-ee2a-sec2a', 'EE 2nd Year A', 40, 'dept-ee-dept-ee-dept-ee-depteedept')
ON CONFLICT (id) DO NOTHING;

-- Insert section subject requirements
INSERT INTO section_subject_requirements (section_id, subject_id, sessions_per_week, session_duration_minutes) VALUES
    -- CSE 3rd Year A
    ('sec-cs3a-sec-cs3a-sec-cs3a-sec3a', 'sub-ds-sub-ds-sub-ds-subdsdsdsds', 3, 60),  -- Data Structures: 3x 60min
    ('sec-cs3a-sec-cs3a-sec-cs3a-sec3a', 'sub-os-sub-os-sub-os-subososos', 2, 90),  -- Operating Systems: 2x 90min
    ('sec-cs3a-sec-cs3a-sec-cs3a-sec3a', 'sub-ca-sub-ca-sub-ca-subcacaca', 2, 60),  -- Linear Algebra: 2x 60min
    -- EE 2nd Year A
    ('sec-ee2a-sec-ee2a-sec-ee2a-sec2a', 'sub-ee-sub-ee-sub-ee-subeesubs', 3, 90),  -- Circuit Analysis: 3x 90min
    ('sec-ee2a-sec-ee2a-sec-ee2a-sec2a', 'sub-ca-sub-ca-sub-ca-subcacaca', 2, 60)   -- Linear Algebra: 2x 60min
ON CONFLICT (section_id, subject_id) DO NOTHING;