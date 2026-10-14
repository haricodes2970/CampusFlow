import os
from typing import List, Dict, Any, Optional
from supabase import create_client, Client
from app.models import (
    Department, Room, Faculty, Subject, Section, Session,
    Timetable, DayOfWeek, Equipment, Availability, SubjectRequirement
)
from app.scheduler import generate_timetable

class SupabaseStore:
    def __init__(self, url: str, key: str):
        self.client: Client = create_client(url, key)
        self.use_db = True

    def _fetch_departments(self) -> List[Department]:
        res = self.client.table("departments").select("*").execute()
        return [
            Department(
                id=d["id"],
                name=d["name"],
                code=d["code"],
                college_id=d["college_id"]
            ) for d in res.data
        ]

    def _fetch_rooms(self) -> List[Room]:
        res = self.client.table("rooms").select("*").execute()
        return [
            Room(
                id=r["id"],
                name=r["name"],
                building=r["building"],
                capacity=r["capacity"],
                equipment=[Equipment(e) for e in r.get("equipment", [])],
                department_id=r["department_id"]
            ) for r in res.data
        ]

    def _fetch_faculty(self) -> List[Faculty]:
        fac_res = self.client.table("faculty").select("*").execute()
        avail_res = self.client.table("faculty_availability").select("*").execute()
        
        avail_map = {}
        for a in avail_res.data:
            fid = a["faculty_id"]
            if fid not in avail_map:
                avail_map[fid] = []
            avail_map[fid].append(
                Availability(
                    day=DayOfWeek(a["day_of_week"]),
                    start_time=str(a["start_time"])[:5],
                    end_time=str(a["end_time"])[:5]
                )
            )

        return [
            Faculty(
                id=f["id"],
                name=f["name"],
                email=f["email"],
                qualifications=f.get("qualifications", []),
                max_hours_per_week=f["max_hours_per_week"],
                availability=avail_map.get(f["id"], []),
                department_id=f["department_id"]
            ) for f in fac_res.data
        ]

    def _fetch_subjects(self) -> List[Subject]:
        res = self.client.table("subjects").select("*").execute()
        return [
            Subject(
                id=s["id"],
                code=s["code"],
                name=s["name"],
                required_equipment=[Equipment(e) for e in s.get("required_equipment", [])],
                min_room_capacity=s["min_room_capacity"],
                qualified_faculty_ids=s.get("qualified_faculty_ids", []),
                department_id=s["department_id"]
            ) for s in res.data
        ]

    def _fetch_sections(self) -> List[Section]:
        sec_res = self.client.table("sections").select("*").execute()
        req_res = self.client.table("section_subject_requirements").select("*").execute()

        req_map = {}
        for r in req_res.data:
            sec_id = r["section_id"]
            if sec_id not in req_map:
                req_map[sec_id] = []
            req_map[sec_id].append(
                SubjectRequirement(
                    subject_id=r["subject_id"],
                    sessions_per_week=r["sessions_per_week"],
                    session_duration_minutes=r["session_duration_minutes"]
                )
            )

        return [
            Section(
                id=s["id"],
                name=s["name"],
                student_count=s["student_count"],
                department_id=s["department_id"],
                subject_requirements=req_map.get(s["id"], [])
            ) for s in sec_res.data
        ]

    def _fetch_sessions(self) -> List[Session]:
        res = self.client.table("timetable_sessions").select("*").execute()
        return [
            Session(
                id=s["id"],
                subject_id=s["subject_id"],
                faculty_id=s["faculty_id"],
                room_id=s["room_id"],
                section_id=s["section_id"],
                day=DayOfWeek(s["day_of_week"]),
                start_slot=s["start_slot"],
                duration_slots=s["duration_slots"]
            ) for s in res.data
        ]

    def get_departments(self) -> List[Department]:
        return self._fetch_departments()

    def add_department(self, dept: Department) -> Department:
        self.client.table("departments").insert(dept.model_dump()).execute()
        return dept

    def update_department(self, dept_id: str, dept: Department) -> Department:
        self.client.table("departments").update(dept.model_dump()).eq("id", dept_id).execute()
        return dept

    def delete_department(self, dept_id: str):
        self.client.table("departments").delete().eq("id", dept_id).execute()

    def get_rooms(self) -> List[Room]:
        return self._fetch_rooms()

    def add_room(self, room: Room) -> Room:
        data = room.model_dump()
        data["equipment"] = [e.value if hasattr(e, "value") else e for e in data.get("equipment", [])]
        self.client.table("rooms").insert(data).execute()
        return room

    def update_room(self, room_id: str, room: Room) -> Room:
        data = room.model_dump()
        data["equipment"] = [e.value if hasattr(e, "value") else e for e in data.get("equipment", [])]
        self.client.table("rooms").update(data).eq("id", room_id).execute()
        return room

    def delete_room(self, room_id: str):
        self.client.table("rooms").delete().eq("id", room_id).execute()

    def get_faculty(self) -> List[Faculty]:
        return self._fetch_faculty()

    def add_faculty(self, fac: Faculty) -> Faculty:
        data = fac.model_dump()
        avail = data.pop("availability", [])
        self.client.table("faculty").insert(data).execute()
        for a in avail:
            self.client.table("faculty_availability").insert({
                "faculty_id": fac.id,
                "day_of_week": a["day"],
                "start_time": a["start_time"],
                "end_time": a["end_time"]
            }).execute()
        return fac

    def update_faculty(self, faculty_id: str, fac: Faculty) -> Faculty:
        data = fac.model_dump()
        avail = data.pop("availability", [])
        self.client.table("faculty").update(data).eq("id", faculty_id).execute()
        # Refresh availability
        self.client.table("faculty_availability").delete().eq("faculty_id", faculty_id).execute()
        for a in avail:
            self.client.table("faculty_availability").insert({
                "faculty_id": faculty_id,
                "day_of_week": a["day"],
                "start_time": a["start_time"],
                "end_time": a["end_time"]
            }).execute()
        return fac

    def delete_faculty(self, faculty_id: str):
        self.client.table("faculty").delete().eq("id", faculty_id).execute()

    def get_subjects(self) -> List[Subject]:
        return self._fetch_subjects()

    def add_subject(self, sub: Subject) -> Subject:
        data = sub.model_dump()
        data["required_equipment"] = [e.value if hasattr(e, "value") else e for e in data.get("required_equipment", [])]
        self.client.table("subjects").insert(data).execute()
        return sub

    def update_subject(self, subject_id: str, sub: Subject) -> Subject:
        data = sub.model_dump()
        data["required_equipment"] = [e.value if hasattr(e, "value") else e for e in data.get("required_equipment", [])]
        self.client.table("subjects").update(data).eq("id", subject_id).execute()
        return sub

    def delete_subject(self, subject_id: str):
        self.client.table("subjects").delete().eq("id", subject_id).execute()

    def get_sections(self) -> List[Section]:
        return self._fetch_sections()

    def add_section(self, sec: Section) -> Section:
        data = sec.model_dump()
        reqs = data.pop("subject_requirements", [])
        self.client.table("sections").insert(data).execute()
        for r in reqs:
            self.client.table("section_subject_requirements").insert({
                "section_id": sec.id,
                "subject_id": r["subject_id"],
                "sessions_per_week": r["sessions_per_week"],
                "session_duration_minutes": r["session_duration_minutes"]
            }).execute()
        return sec

    def update_section(self, section_id: str, sec: Section) -> Section:
        data = sec.model_dump()
        reqs = data.pop("subject_requirements", [])
        self.client.table("sections").update(data).eq("id", section_id).execute()
        self.client.table("section_subject_requirements").delete().eq("section_id", section_id).execute()
        for r in reqs:
            self.client.table("section_subject_requirements").insert({
                "section_id": section_id,
                "subject_id": r["subject_id"],
                "sessions_per_week": r["sessions_per_week"],
                "session_duration_minutes": r["session_duration_minutes"]
            }).execute()
        return sec

    def delete_section(self, section_id: str):
        self.client.table("sections").delete().eq("id", section_id).execute()

    def get_sessions(self) -> List[Session]:
        return self._fetch_sessions()

    def add_session(self, session: Session) -> Session:
        data = {
            "id": session.id,
            "subject_id": session.subject_id,
            "faculty_id": session.faculty_id,
            "room_id": session.room_id,
            "section_id": session.section_id,
            "day_of_week": session.day.value if hasattr(session.day, "value") else session.day,
            "start_slot": session.start_slot,
            "duration_slots": session.duration_slots
        }
        self.client.table("timetable_sessions").insert(data).execute()
        return session

    def update_session(self, session_id: str, session: Session) -> Session:
        data = {
            "subject_id": session.subject_id,
            "faculty_id": session.faculty_id,
            "room_id": session.room_id,
            "section_id": session.section_id,
            "day_of_week": session.day.value if hasattr(session.day, "value") else session.day,
            "start_slot": session.start_slot,
            "duration_slots": session.duration_slots
        }
        self.client.table("timetable_sessions").update(data).eq("id", session_id).execute()
        return session

    def delete_session(self, session_id: str):
        self.client.table("timetable_sessions").delete().eq("id", session_id).execute()

    def clear_sessions(self):
        self.client.table("timetable_sessions").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()

    def get_timetable(self) -> Timetable:
        sessions = self.get_sessions()
        # Generate unscheduled report by running scheduler against current master data
        depts = self.get_departments()
        rooms = self.get_rooms()
        fac = self.get_faculty()
        subs = self.get_subjects()
        secs = self.get_sections()
        
        # We can re-run generation or evaluate unscheduled
        res = generate_timetable(depts, rooms, fac, subs, secs)
        return Timetable(sessions=sessions, unscheduled=res.unscheduled)

    def run_generation(self) -> Timetable:
        depts = self.get_departments()
        rooms = self.get_rooms()
        fac = self.get_faculty()
        subs = self.get_subjects()
        secs = self.get_sections()
        
        result = generate_timetable(depts, rooms, fac, subs, secs)
        
        # Persist generated sessions to DB
        self.clear_sessions()
        for session in result.sessions:
            self.add_session(session)
            
        return Timetable(sessions=result.sessions, unscheduled=result.unscheduled)
