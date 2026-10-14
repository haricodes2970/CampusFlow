import { useState, useEffect } from 'react';
import { api } from '../api';
import type { Stats, UnscheduledSession } from '../types';

interface Props {
  onNavigate: (k: 'departments' | 'rooms' | 'faculty' | 'subjects' | 'sections' | 'timetable') => void;
  onError: (title: string, msg: string, details?: string[]) => void;
  onSuccess: (title: string, msg?: string) => void;
}

export function DashboardView({ onNavigate, onError, onSuccess }: Props) {
  const [stats, setStats] = useState<Stats | null>(null);
  const [unscheduled, setUnscheduled] = useState<UnscheduledSession[]>([]);
  const [loading, setLoading] = useState(false);

  const loadData = async () => {
    try {
      const [st, un] = await Promise.all([
        api.stats(),
        api.getUnscheduled(),
      ]);
      setStats(st);
      setUnscheduled(un);
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
        <div style={{display: 'flex', gap: 10, alignItems: 'center'}}>
          <div className="chip" style={{background: 'rgba(52,211,153,0.14)', color: '#6ee7b7', borderColor: 'rgba(52,211,153,0.3)'}}>
            🟢 Local Demo Persistence Active
          </div>
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

      {/* 3-Minute Demo Guide Box */}
      <div className="glass panel" style={{borderColor: 'rgba(139,92,246,0.3)', background: 'rgba(139,92,246,0.04)'}}>
        <div className="panel-head">
          <div className="panel-title">
            <h2>🚀 3-Minute Demo Walkthrough Guide</h2>
          </div>
        </div>
        <ol style={{margin: '0 0 0 18px', padding: 0, color: 'var(--text-dim)', fontSize: '0.85rem', display: 'flex', flexDirection: 'column', gap: 6}}>
          <li><strong>Step 1 (Dashboard):</strong> Review real-time metrics and active unscheduled conflict reports above.</li>
          <li><strong>Step 2 (Data Management):</strong> Click any stat card or sidebar item (e.g. <em>Rooms</em> or <em>Faculty</em>) to inspect and manage core academic records.</li>
          <li><strong>Step 3 (Scheduling Engine):</strong> Go to <em>Timetable</em> or click <strong>Generate Timetable</strong> to run the deterministic constraint solver.</li>
          <li><strong>Step 4 (Constraint Enforcement):</strong> Notice how hard constraints (capacity, faculty availability, equipment) prevent invalid assignments and report clear reasons instead of failing silently.</li>
          <li><strong>Step 5 (Validated Editing):</strong> Add or modify a session directly in the Timetable view and observe real-time validation feedback.</li>
        </ol>
      </div>

      <div className="glass panel">
        <div className="panel-head">
          <div className="panel-title">
            <h2>⚠️ Unscheduled Sessions & Constraint Explanations</h2>
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