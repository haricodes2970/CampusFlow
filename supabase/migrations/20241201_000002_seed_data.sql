-- CampusFlow Seed Data Migration (Corrected with Valid UUIDs)
-- Inserts realistic demo data with valid, RFC-compliant UUID identifiers
-- Uses a PL/pgSQL DO block to scope deterministic UUID constants across all INSERTs
-- Uses ON CONFLICT on actual unique constraints for idempotency

DO $$
DECLARE
    -- Deterministic UUID constants (namespace: 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa')
    college_main_id   uuid := '28aacd16-a4c9-5df7-b0ad-3e6791115770';
    dept_cs_id        uuid := '6c69ad66-b901-58d8-bca5-80f4c179bc43';
    dept_ee_id        uuid := '6c0142a9-62ff-5056-b6b6-b17e77846768';
    dept_ma_id        uuid := '6f9957a2-85e3-516c-87bc-1750930e7741';
    room_101_id       uuid := '98d2185f-af82-5929-bb50-3446a017b2a6';
    room_102_id       uuid := '563ae681-86f1-5f8d-9a5d-746d08f0a20c';
    room_201_id       uuid := '143162ae-39ff-5f16-919b-2b2eb15b28e8';
    room_301_id       uuid := '9363b75d-b55c-555c-9047-cb84a0632a7f';
    fac_1_id          uuid := '7ce6104e-02c0-529d-ab67-4d9272ec98be';
    fac_2_id          uuid := '0a3653a2-253e-51b8-a718-611a5b48946c';
    fac_3_id          uuid := 'fa9b81a5-c554-53ae-9f0f-3a03d79779ea';
    fac_4_id          uuid := '135f9526-2479-53ea-9a9c-f8944b7803fa';
    sub_ds_id         uuid := '21cf24ed-9f62-54c1-810b-52e4d4c2d022';
    sub_os_id         uuid := 'f769efc8-d411-5816-8ec8-2752f0801972';
    sub_ee_id         uuid := '4fa9b925-39b5-5309-994e-13bc6797fcc4';
    sub_ca_id         uuid := '99938e86-cdb3-5231-ab8b-f840d8aae8bf';
    sec_cs3a_id       uuid := 'a9b6e6b2-f367-520e-9313-ea76de80ecf9';
    sec_ee2a_id       uuid := '9fb644a1-673e-5602-bee6-b3bad94fc3e3';
BEGIN
    -- ============================================
    -- 1. COLLEGE
    -- ============================================
    INSERT INTO colleges (id, name, code)
    VALUES (college_main_id, 'Main Campus University', 'MAIN')
    ON CONFLICT (code) DO NOTHING;

    -- ============================================
    -- 2. DEPARTMENTS
    -- ============================================
    INSERT INTO departments (id, name, code, college_id)
    VALUES
        (dept_cs_id, 'Computer Science & Engineering', 'CSE', college_main_id),
        (dept_ee_id, 'Electrical Engineering', 'EE', college_main_id),
        (dept_ma_id, 'Mathematics', 'MATH', college_main_id)
    ON CONFLICT (college_id, code) DO NOTHING;

    -- ============================================
    -- 3. ROOMS
    -- ============================================
    INSERT INTO rooms (id, name, building, capacity, equipment, department_id)
    VALUES
        (room_101_id, 'Lab 101', 'Science Block', 60, ARRAY['PROJECTOR','COMPUTERS','WHITEBOARD'], dept_cs_id),
        (room_102_id, 'Lecture Hall A', 'Science Block', 120, ARRAY['PROJECTOR','AUDIO_SYSTEM','WHITEBOARD'], dept_cs_id),
        (room_201_id, 'EE Lab 201', 'Engineering Hall', 45, ARRAY['PROJECTOR','COMPUTERS'], dept_ee_id),
        (room_301_id, 'Math Hall 301', 'Arts Building', 90, ARRAY['WHITEBOARD','SMART_BOARD'], dept_ma_id)
    ON CONFLICT (id) DO NOTHING;

    -- ============================================
    -- 4. FACULTY
    -- ============================================
    INSERT INTO faculty (id, name, email, qualifications, max_hours_per_week, department_id)
    VALUES
        (fac_1_id, 'Dr. Alan Turing', 'turing@campusflow.edu', ARRAY['Algorithms','Data Structures','AI'], 18, dept_cs_id),
        (fac_2_id, 'Prof. Grace Hopper', 'hopper@campusflow.edu', ARRAY['Operating Systems','Compilers','Data Structures'], 20, dept_cs_id),
        (fac_3_id, 'Dr. Nikola Tesla', 'tesla@campusflow.edu', ARRAY['Circuit Analysis','Electromagnetism'], 16, dept_ee_id),
        (fac_4_id, 'Dr. Katherine Johnson', 'johnson@campusflow.edu', ARRAY['Linear Algebra','Calculus','Differential Equations'], 20, dept_ma_id)
    ON CONFLICT (email) DO NOTHING;

    -- ============================================
    -- 5. FACULTY AVAILABILITY
    -- ============================================
    INSERT INTO faculty_availability (faculty_id, day_of_week, start_time, end_time)
    VALUES
        (fac_1_id, 'MONDAY', '09:00'::time, '17:00'::time),
        (fac_1_id, 'WEDNESDAY', '09:00'::time, '17:00'::time),
        (fac_1_id, 'FRIDAY', '09:00'::time, '17:00'::time),
        (fac_2_id, 'TUESDAY', '08:00'::time, '16:00'::time),
        (fac_2_id, 'THURSDAY', '08:00'::time, '16:00'::time),
        (fac_3_id, 'MONDAY', '10:00'::time, '15:00'::time),
        (fac_3_id, 'WEDNESDAY', '10:00'::time, '15:00'::time),
        (fac_4_id, 'MONDAY', '09:00'::time, '17:00'::time),
        (fac_4_id, 'TUESDAY', '09:00'::time, '17:00'::time),
        (fac_4_id, 'WEDNESDAY', '09:00'::time, '17:00'::time),
        (fac_4_id, 'THURSDAY', '09:00'::time, '17:00'::time),
        (fac_4_id, 'FRIDAY', '09:00'::time, '17:00'::time)
    ON CONFLICT (faculty_id, day_of_week, start_time, end_time) DO NOTHING;

    -- ============================================
    -- 6. SUBJECTS
    -- ============================================
    INSERT INTO subjects (id, code, name, required_equipment, min_room_capacity, qualified_faculty_ids, department_id)
    VALUES
        (sub_ds_id, 'CS201', 'Data Structures & Algorithms', ARRAY['PROJECTOR','COMPUTERS'], 50, ARRAY[fac_1_id, fac_2_id], dept_cs_id),
        (sub_os_id, 'CS301', 'Operating Systems', ARRAY['PROJECTOR','WHITEBOARD'], 100, ARRAY[fac_2_id], dept_cs_id),
        (sub_ee_id, 'EE101', 'Circuit Analysis', ARRAY['PROJECTOR','COMPUTERS'], 40, ARRAY[fac_3_id], dept_ee_id),
        (sub_ca_id, 'MA101', 'Linear Algebra & Calculus', ARRAY['WHITEBOARD'], 80, ARRAY[fac_4_id], dept_ma_id)
    ON CONFLICT (department_id, code) DO NOTHING;

    -- ============================================
    -- 7. SECTIONS
    -- ============================================
    INSERT INTO sections (id, name, student_count, department_id)
    VALUES
        (sec_cs3a_id, 'CSE 3rd Year A', 55, dept_cs_id),
        (sec_ee2a_id, 'EE 2nd Year A', 40, dept_ee_id)
    ON CONFLICT (id) DO NOTHING;

    -- ============================================
    -- 8. SECTION SUBJECT REQUIREMENTS
    -- ============================================
    INSERT INTO section_subject_requirements (section_id, subject_id, sessions_per_week, session_duration_minutes)
    VALUES
        (sec_cs3a_id, sub_ds_id, 3, 60),
        (sec_cs3a_id, sub_os_id, 2, 90),
        (sec_cs3a_id, sub_ca_id, 2, 60),
        (sec_ee2a_id, sub_ee_id, 3, 90),
        (sec_ee2a_id, sub_ca_id, 2, 60)
    ON CONFLICT (section_id, subject_id) DO NOTHING;

END $$;