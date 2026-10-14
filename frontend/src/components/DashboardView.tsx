import { useState, useEffect } from 'react';
import { api } from '../api';
import type { Stats, UnscheduledSession } from '../types';
import { getSubjectCode, getSectionName } from '../utils';

interface Props {
  onNavigate: (k: 'departments' | 'rooms' | 'faculty' | 'subjects' | 'sections' | 'timetable') => void;
  onError: (title: string, msg: string, details?: string[]) => void;
  onSuccess: (title: string, msg?: string) => void;
}

export function DashboardView({ onNavigate, onError, onSuccess }: Props) {
  const [stats, setStats] = useState<Stats | null>(null);
  const [unscheduled, setUnscheduled] = useState<UnscheduledSession[]>([]);
  const [subjects, setSubjects] = useState<any[]>([]);
  const [sections, setSections] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const loadData = async () => {
    try {
      const [st, un, subs, secs] = await Promise.all([
        api.stats(),
        api.getUnscheduled(),
        api.listSubjects(),
        api.listSections(),
      ]);
      setStats(st);
      setUnscheduled(un);
      setSubjects(subs);
      setSections(secs);
    } catch (e: any) {
      onError('Failed to load dashboard', e.message);
    }
  };

  useEffect(() => { loadData(); }, []);

  const handleGenerate = async () => {
    setLoading(true);
    try {
      await api.generate();
      await loadData();
      onSuccess('Timetable Generated', 'Successfully ran scheduling algorithm and validated constraints.');
    } catch (e: any) {
      onError('Generation Failed', e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="topbar">
        <div>
          <h1>Dashboard & Overview</h1>
          <div className="topbar-sub">CampusFlow academic administration and automated scheduler</div>
        </div>
        <div style={{display: 'flex', gap: 10}}>
          <button className="btn cyan" onClick={handleGenerate} disabled={loading}>
            {loading ? 'Generating...' : '⚡ Generate Timetable'}
          </button>
        </div>
      </div>

      {stats ? (
        <div className="stat-grid">
          <div className="glass stat" onClick={() => onNavigate('departments')} style={{cursor: 'pointer'}}>
            <div className="stat-label">Departments</div>
            <div className="stat-value">{stats.departments}</div>
            <div className="stat-foot">Active academic units</div>
          </div>
          <div className="glass stat" onClick={() => onNavigate('rooms')} style={{cursor: 'pointer'}}>
            <div className="stat-label">Rooms & Labs</div>
            <div className="stat-value">{stats.rooms}</div>
            <div className="stat-foot">Allocatable spaces</div>
          </div>
          <div className="glass stat" onClick={() => onNavigate('faculty')} style={{cursor: 'pointer'}}>
            <div className="stat-label">Faculty</div>
            <div className="stat-value">{stats.faculty}</div>
            <div className="stat-foot">Qualified instructors</div>
          </div>
          <div className="glass stat" onClick={() => onNavigate('subjects')} style={{cursor: 'pointer'}}>
            <div className="stat-label">Subjects</div>
            <div className="stat-value">{stats.subjects}</div>
            <div className="stat-foot">Curriculum courses</div>
          </div>
          <div className="glass stat" onClick={() => onNavigate('sections')} style={{cursor: 'pointer'}}>
            <div className="stat-label">Sections</div>
            <div className="stat-value">{stats.sections}</div>
            <div className="stat-foot">Student cohorts</div>
          </div>
          <div className="glass stat" onClick={() => onNavigate('timetable')} style={{cursor: 'pointer'}}>
            <div className="stat-label">Scheduled Sessions</div>
            <div className="stat-value" style={{color: 'var(--cyan-bright)'}}>{stats.scheduled_sessions}</div>
            <div className="stat-foot">Valid allocations</div>
          </div>
          <div className="glass stat" onClick={() => onNavigate('timetable')} style={{cursor: 'pointer'}}>
            <div className="stat-label">Unscheduled Sessions</div>
            <div className="stat-value warn">{stats.unscheduled_sessions}</div>
            <div className="stat-foot">Conflict report</div>
          </div>
        </div>
      ) : (
        <div className="loading"><div className="spinner"></div>Loading dashboard metrics...</div>
      )}

      <div className="glass panel">
        <div className="panel-head">
          <div className="panel-title">
            <h2>⚠️ Unscheduled Sessions & Conflict Report</h2>
          </div>
          <button className="btn sm ghost" onClick={loadData}>Refresh</button>
        </div>

        {unscheduled.length === 0 ? (
          <div className="empty" style={{padding: '20px 0'}}>
            🎉 Zero unscheduled sessions! All curriculum requirements fully satisfied without hard-constraint violations.
          </div>
        ) : (
          <div>
            <div className="muted" style={{marginBottom: 12}}>
              The deterministic scheduler halted rather than silently violating hard constraints (capacity, faculty availability, equipment, or overlaps).
            </div>
            {unscheduled.map((u, i) => (
              <div key={i} className="unsched-item">
                <div className="unsched-head">
                  <strong>{u.subject_name}</strong> ({u.section_name})
                  <span className="chip warn">
                    Scheduled {u.scheduled_sessions} / {u.required_sessions} required sessions
                  </span>
                </div>
                <ul className="unsched-reasons">
                  {u.violations.map((v, idx) => (
                    <li key={idx}><strong>{v.type}:</strong> {v.message}</li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}