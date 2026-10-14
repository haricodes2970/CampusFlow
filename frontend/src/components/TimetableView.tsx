import { useState, useEffect, useCallback } from 'react';
import { api } from '../api';
import type { Session, Subject, Faculty, Room, Section, Timetable } from '../types';
import { useToast } from './Toast';
import {
  DAYS, DAY_LABELS, SLOT_DURATION, VISIBLE_START_SLOT, VISIBLE_END_SLOT,
  timeToSlot, slotToTime, formatSlotRange, getSessionColor,
  getSubjectCode, getFacultyName, getRoomName, getSectionName,
  isSessionOverlapping
} from '../utils';

interface Props {
  onError: (title: string, msg: string, details?: string[]) => void;
  onSuccess: (title: string, msg?: string) => void;
}

const SLOTS = Array.from({ length: VISIBLE_END_SLOT - VISIBLE_START_SLOT }, (_, i) => VISIBLE_START_SLOT + i);

export function TimetableView({ onError, onSuccess }: Props) {
  const [timetable, setTimetable] = useState<Timetable | null>(null);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [faculty, setFaculty] = useState<Faculty[]>([]);
  const [rooms, setRooms] = useState<Room[]>([]);
  const [sections, setSections] = useState<Section[]>([]);
  const [filterSection, setFilterSection] = useState<string>('all');
  const [filterDay, setFilterDay] = useState<string>('all');
  const [loading, setLoading] = useState(false);
  const { success, error } = useToast();

  const loadData = useCallback(async () => {
    try {
      const [tt, subs, facs, rms, secs] = await Promise.all([
        api.getTimetable(),
        api.listSubjects(),
        api.listFaculty(),
        api.listRooms(),
        api.listSections(),
      ]);
      setTimetable(tt);
      setSubjects(subs);
      setFaculty(facs);
      setRooms(rms);
      setSections(secs);
    } catch (e: any) {
      onError('Load Failed', e.message);
    }
  }, [onError]);

  useEffect(() => { loadData(); }, [loadData]);

  const getSessions = () => {
    if (!timetable) return [];
    let sessions = timetable.sessions;
    if (filterSection !== 'all') sessions = sessions.filter(s => s.section_id === filterSection);
    if (filterDay !== 'all') sessions = sessions.filter(s => s.day === filterDay);
    return sessions;
  };

  const getCellSessions = (day: string, slot: number) => {
    return getSessions().filter(s => s.day === day && s.start_slot <= slot && s.start_slot + s.duration_slots > slot);
  };

  const hasConflict = (day: string, slot: number) => {
    const cellSessions = getCellSessions(day, slot);
    if (cellSessions.length <= 1) return false;
    // Check for conflicts among overlapping sessions
    for (let i = 0; i < cellSessions.length; i++) {
      for (let j = i + 1; j < cellSessions.length; j++) {
        if (isSessionOverlapping(cellSessions[i], cellSessions[j])) return true;
      }
    }
    return false;
  };

  const handleCreateSession = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    try {
      await api.createSession({
        subject_id: fd.get('subject_id') as string,
        faculty_id: fd.get('faculty_id') as string,
        room_id: fd.get('room_id') as string,
        section_id: fd.get('section_id') as string,
        day: fd.get('day') as any,
        start_time: fd.get('start_time') as string,
        duration_minutes: parseInt(fd.get('duration_minutes') as string) || 60,
      });
      success('Session Added', 'Validated and added to timetable');
      loadData();
    } catch (e: any) {
      if (e.message.includes('violations')) {
        try {
          const { violations } = JSON.parse(e.message.replace('violations: ', ''));
          error('Constraint Violation', 'Cannot add session - hard constraints violated',
            violations.map((v: any) => `${v.type}: ${v.message}`));
        } catch {
          error('Constraint Violation', e.message);
        }
      } else {
        error('Add Failed', e.message);
      }
    }
  };

  const handleDeleteSession = async (id: string) => {
    if (!confirm('Remove this session from the timetable?')) return;
    try {
      await api.deleteSession(id);
      success('Session Removed');
      loadData();
    } catch (e: any) {
      error('Delete Failed', e.message);
    }
  };

  if (!timetable) return <div className="loading"><div className="spinner"></div>Loading timetable...</div>;

  return (
    <div>
      <div className="topbar">
        <div>
          <h1>Weekly Timetable</h1>
          <div className="topbar-sub">Validated schedule with conflict detection and constraint-aware editing</div>
        </div>
        <div style={{display: 'flex', gap: 10, flexWrap: 'wrap', alignItems: 'center'}}>
          <select className="field" value={filterSection} onChange={e => setFilterSection(e.target.value)}>
            <option value="all">All Sections</option>
            {sections.map(s => <option key={s.id} value={s.id}>{s.name} ({s.student_count})</option>)}
          </select>
          <select className="field" value={filterDay} onChange={e => setFilterDay(e.target.value)}>
            <option value="all">All Days</option>
            {DAYS.map(d => <option key={d} value={d}>{DAY_LABELS[d]}</option>)}
          </select>
          <button className="btn cyan" onClick={loadData}>🔄 Refresh</button>
        </div>
      </div>

      {/* Add Session Form */}
      <div className="glass panel" style={{marginBottom: 18}}>
        <div className="panel-head"><div className="panel-title"><h2>➕ Add Validated Session</h2></div></div>
        <form onSubmit={handleCreateSession} style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 12}}>
          <div className="field">
            <label>Subject</label>
            <select name="subject_id" required>
              <option value="">Select...</option>
              {subjects.map(s => <option key={s.id} value={s.id}>{s.code} – {s.name}</option>)}
            </select>
          </div>
          <div className="field">
            <label>Faculty</label>
            <select name="faculty_id" required>
              <option value="">Select...</option>
              {faculty.map(f => <option key={f.id} value={f.id}>{f.name}</option>)}
            </select>
          </div>
          <div className="field">
            <label>Room</label>
            <select name="room_id" required>
              <option value="">Select...</option>
              {rooms.map(r => <option key={r.id} value={r.id}>{r.name} (cap {r.capacity})</option>)}
            </select>
          </div>
          <div className="field">
            <label>Section</label>
            <select name="section_id" required>
              <option value="">Select...</option>
              {sections.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
            </select>
          </div>
          <div className="field">
            <label>Day</label>
            <select name="day" required>
              <option value="">Select...</option>
              {DAYS.map(d => <option key={d} value={d}>{DAY_LABELS[d]}</option>)}
            </select>
          </div>
          <div className="field">
            <label>Start Time</label>
            <input type="time" name="start_time" required />
          </div>
          <div className="field">
            <label>Duration (min)</label>
            <select name="duration_minutes">
              <option value="30">30</option>
              <option value="60" selected>60</option>
              <option value="90">90</option>
              <option value="120">120</option>
            </select>
          </div>
          <div className="field" style={{gridColumn: '1 / -1', display: 'flex', gap: 10, alignItems: 'end'}}>
            <button type="submit" className="btn primary">Add Session (Validated)</button>
          </div>
        </form>
      </div>

      {/* Timetable Grid */}
      <div className="glass panel">
        <div className="panel-head"><div className="panel-title"><h2>Grid View (07:00–19:00)</h2></div></div>
        <div className="tt-scroll">
          <div className="tt-grid" style={{gridTemplateColumns: `60px repeat(${DAYS.length}, 1fr)`}}>
            <div className="tt-head">Time</div>
            {DAYS.map(d => <div key={d} className="tt-head">{DAY_LABELS[d]}</div>)}

            {SLOTS.map(slot => (
              <>
                <div key={`time-${slot}`} className="tt-time">{slotToTime(slot)}</div>
                {DAYS.map(day => {
                  const cellSessions = getCellSessions(day, slot);
                  const isFirstSlot = cellSessions.some(s => s.start_slot === slot);
                  const conflict = hasConflict(day, slot);

                  if (!isFirstSlot && cellSessions.length > 0) {
                    return <div key={`${day}-${slot}`} className="tt-cell" />;
                  }

                  if (cellSessions.length === 0) {
                    return (
                      <div key={`${day}-${slot}`} className="tt-cell" />
                    );
                  }

                  // Multiple sessions in same cell (should not happen with validation, but show anyway)
                  return (
                    <div key={`${day}-${slot}`} className="tt-cell occupied">
                      {cellSessions.map(s => (
                        <div
                          key={s.id}
                          className={`tt-session ${conflict ? 'conflict' : ''}`}
                          style={{
                            background: getSessionColor(s.subject_id),
                            borderColor: getSessionColor(s.subject_id),
                          }}
                        >
                          <span className="s-subj">{getSubjectCode(subjects, s.subject_id)}</span>
                          <span className="s-meta">{getFacultyName(faculty, s.faculty_id)}</span>
                          <span className="s-room">{getRoomName(rooms, s.room_id)}</span>
                        </div>
                      ))}
                    </div>
                  );
                })}
              </>
            ))}
          </div>
        </div>

        <div className="muted" style={{marginTop: 12, fontSize: '0.75rem'}}>
          Legend: Colored blocks = scheduled sessions. Each block shows subject code, faculty, and room.
          Red pulse = detected hard-constraint conflict. Grid shows 30-min slots from 07:00–19:00.
        </div>
      </div>

      {/* Session List */}
      <div className="glass panel table-wrap">
        <div className="panel-head"><div className="panel-title"><h2>Scheduled Sessions ({timetable.sessions.length})</h2></div></div>
        <table>
          <thead>
            <tr>
              <th>Subject</th><th>Section</th><th>Faculty</th><th>Room</th><th>Day</th><th>Time</th><th>Duration</th><th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {getSessions().map(s => (
              <tr key={s.id}>
                <td>{getSubjectCode(subjects, s.subject_id)}</td>
                <td>{getSectionName(sections, s.section_id)}</td>
                <td>{getFacultyName(faculty, s.faculty_id)}</td>
                <td>{getRoomName(rooms, s.room_id)}</td>
                <td>{DAY_LABELS[s.day]}</td>
                <td className="mono">{slotToTime(s.start_slot)}</td>
                <td>{s.duration_slots * SLOT_DURATION}min</td>
                <td style={{textAlign: 'center'}}>
                  <button className="btn ghost sm danger" onClick={() => handleDeleteSession(s.id)}>✕</button>
                </td>
              </tr>
            ))}
            {getSessions().length === 0 && (
              <tr><td colSpan={8} className="empty">No sessions match current filters.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}