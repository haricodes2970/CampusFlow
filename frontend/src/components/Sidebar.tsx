import { useState, useEffect } from 'react';
import { api } from '../api';
import type { Stats } from '../types';

type NavKey = 'dashboard' | 'departments' | 'rooms' | 'faculty' | 'subjects' | 'sections' | 'timetable';

interface Props {
  active: NavKey;
  onChange: (k: NavKey) => void;
}

export function Sidebar({ active, onChange }: Props) {
  const [stats, setStats] = useState<Stats | null>(null);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    api.stats().then(s => { setStats(s); setConnected(true); })
      .catch(() => setConnected(false));
  }, []);

  const navItems: { key: NavKey; label: string; icon: string }[] = [
    { key: 'dashboard', label: 'Dashboard', icon: '◦' },
    { key: 'departments', label: 'Departments', icon: '▢' },
    { key: 'rooms', label: 'Rooms', icon: '⬚' },
    { key: 'faculty', label: 'Faculty', icon: '◆' },
    { key: 'subjects', label: 'Subjects', icon: '●' },
    { key: 'sections', label: 'Sections', icon: '◇' },
    { key: 'timetable', label: 'Timetable', icon: '■' },
  ];

  return (
    <aside className="sidebar" role="navigation" aria-label="Main navigation">
      <div className="brand">
        <img src="/logo.svg" alt="CampusFlow Logo" style={{ width: '100%', maxWidth: '170px', height: 'auto', display: 'block', margin: '0 auto 6px' }} />
      </div>

      <nav>
        {navItems.map(item => (
          <button
            key={item.key}
            className={`nav-item ${active === item.key ? 'active' : ''}`}
            onClick={() => onChange(item.key)}
            aria-current={active === item.key ? 'page' : undefined}
          >
            <span className="ico" aria-hidden="true">{item.icon}</span>
            {item.label}
          </button>
        ))}
      </nav>

      <div className="sidebar-foot">
        <span className={`status-dot ${connected ? 'on' : 'off'}`} aria-hidden="true"></span>
        {connected ? 'API connected' : 'API offline'}
        {stats && (
          <>
            {' • '}
            <span className="mono">{stats.scheduled_sessions} sessions</span>
            {' • '}
            <span className="chip warn">{stats.unscheduled_sessions} unscheduled</span>
          </>
        )}
      </div>
    </aside>
  );
}