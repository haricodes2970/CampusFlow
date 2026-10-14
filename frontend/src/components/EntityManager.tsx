import { useState, useEffect, useCallback } from 'react';
import { api } from '../api';
import type { Department, Room, Faculty, Subject, Section } from '../types';
import { useToast } from './Toast';
import { shortId } from '../utils';

type EntityType = 'departments' | 'rooms' | 'faculty' | 'subjects' | 'sections';

const entityConfig: Record<EntityType, {
  label: string;
  fields: { key: string; label: string; type: string; options?: string[] }[];
  list: () => Promise<any[]>;
  create: (d: any) => Promise<any>;
  update: (id: string, d: any) => Promise<any>;
  remove: (id: string) => Promise<any>;
  renderRow: (item: any) => React.ReactNode;
}> = {
  departments: {
    label: 'Departments',
    fields: [
      { key: 'id', label: 'ID', type: 'text', },
      { key: 'name', label: 'Name', type: 'text' },
      { key: 'code', label: 'Code', type: 'text' },
      { key: 'college_id', label: 'College ID', type: 'text' },
    ],
    list: api.listDepartments,
    create: api.createDepartment,
    update: api.updateDepartment,
    remove: api.deleteDepartment,
    renderRow: (d: Department) => (
      <>
        <td>{d.code}</td>
        <td>{d.name}</td>
        <td className="mono">{shortId(d.college_id)}</td>
        <td className="mono">{shortId(d.id)}</td>
      </>
    ),
  },
  rooms: {
    label: 'Rooms & Labs',
    fields: [
      { key: 'id', label: 'ID', type: 'text' },
      { key: 'name', label: 'Name', type: 'text' },
      { key: 'building', label: 'Building', type: 'text' },
      { key: 'capacity', label: 'Capacity', type: 'number' },
      { key: 'equipment', label: 'Equipment (comma)', type: 'text' },
      { key: 'department_id', label: 'Dept ID', type: 'text' },
    ],
    list: api.listRooms,
    create: api.createRoom,
    update: api.updateRoom,
    remove: api.deleteRoom,
    renderRow: (r: Room) => (
      <>
        <td>{r.name}</td>
        <td>{r.building}</td>
        <td>{r.capacity}</td>
        <td><div className="chip-row">{r.equipment.map(e => <span key={e} className="chip cyan">{e}</span>)}</div></td>
        <td className="mono">{shortId(r.department_id)}</td>
        <td className="mono">{shortId(r.id)}</td>
      </>
    ),
  },
  faculty: {
    label: 'Faculty',
    fields: [
      { key: 'id', label: 'ID', type: 'text' },
      { key: 'name', label: 'Name', type: 'text' },
      { key: 'email', label: 'Email', type: 'email' },
      { key: 'qualifications', label: 'Qualifications (comma)', type: 'text' },
      { key: 'max_hours_per_week', label: 'Max Hours/Week', type: 'number' },
      { key: 'availability', label: 'Availability JSON', type: 'textarea' },
      { key: 'department_id', label: 'Dept ID', type: 'text' },
    ],
    list: api.listFaculty,
    create: api.createFaculty,
    update: api.updateFaculty,
    remove: api.deleteFaculty,
    renderRow: (f: Faculty) => (
      <>
        <td>{f.name}</td>
        <td>{f.email}</td>
        <td>{f.max_hours_per_week}</td>
        <td><div className="chip-row">{f.qualifications.map(q => <span key={q} className="chip">{q}</span>)}</div></td>
        <td className="mono">{shortId(f.department_id)}</td>
        <td className="mono">{shortId(f.id)}</td>
      </>
    ),
  },
  subjects: {
    label: 'Subjects',
    fields: [
      { key: 'id', label: 'ID', type: 'text' },
      { key: 'code', label: 'Code', type: 'text' },
      { key: 'name', label: 'Name', type: 'text' },
      { key: 'required_equipment', label: 'Required Equipment (comma)', type: 'text' },
      { key: 'min_room_capacity', label: 'Min Room Capacity', type: 'number' },
      { key: 'qualified_faculty_ids', label: 'Qualified Faculty IDs (comma)', type: 'text' },
      { key: 'department_id', label: 'Dept ID', type: 'text' },
    ],
    list: api.listSubjects,
    create: api.createSubject,
    update: api.updateSubject,
    remove: api.deleteSubject,
    renderRow: (s: Subject) => (
      <>
        <td>{s.code}</td>
        <td>{s.name}</td>
        <td><div className="chip-row">{s.required_equipment.map(e => <span key={e} className="chip cyan">{e}</span>)}</div></td>
        <td>{s.min_room_capacity}</td>
        <td className="mono">{s.qualified_faculty_ids.join(', ') || 'Any'}</td>
        <td className="mono">{shortId(s.department_id)}</td>
        <td className="mono">{shortId(s.id)}</td>
      </>
    ),
  },
  sections: {
    label: 'Student Sections',
    fields: [
      { key: 'id', label: 'ID', type: 'text' },
      { key: 'name', label: 'Name', type: 'text' },
      { key: 'student_count', label: 'Student Count', type: 'number' },
      { key: 'department_id', label: 'Dept ID', type: 'text' },
      { key: 'subject_requirements', label: 'Requirements JSON', type: 'textarea' },
    ],
    list: api.listSections,
    create: api.createSection,
    update: api.updateSection,
    remove: api.deleteSection,
    renderRow: (s: Section) => (
      <>
        <td>{s.name}</td>
        <td>{s.student_count}</td>
        <td className="mono">{shortId(s.department_id)}</td>
        <td>
          <div className="chip-row">
            {s.subject_requirements.map((r: any) => (
              <span key={r.subject_id} className="chip">{r.subject_id} × {r.sessions_per_week} ({r.session_duration_minutes}min)</span>
            ))}
          </div>
        </td>
        <td className="mono">{shortId(s.id)}</td>
      </>
    ),
  },
};

interface Props {
  type: EntityType;
}

export function EntityManager({ type }: Props) {
  const config = entityConfig[type];
  const [items, setItems] = useState<any[]>([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<any | null>(null);
  const [formData, setFormData] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const { success, error } = useToast();

  const load = useCallback(async () => {
    try {
      const data = await config.list();
      setItems(data);
    } catch (e: any) {
      error('Load Failed', e.message);
    }
  }, [config, error]);

  useEffect(() => { load(); }, [load]);

  const openCreate = () => {
    setEditing(null);
    const empty: Record<string, string> = {};
    config.fields.forEach(f => { empty[f.key] = f.type === 'number' ? '0' : ''; });
    setFormData(empty);
    setModalOpen(true);
  };

  const openEdit = (item: any) => {
    setEditing(item);
    const data: Record<string, string> = {};
    config.fields.forEach(f => {
      const val = item[f.key];
      data[f.key] = Array.isArray(val) ? val.join(', ') : String(val ?? '');
    });
    setFormData(data);
    setModalOpen(true);
  };

  const closeModal = () => {
    setModalOpen(false);
    setEditing(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      // Parse form data
      const payload: Record<string, any> = { id: editing?.id };
      config.fields.forEach(f => {
        const raw = formData[f.key]?.trim() || '';
        let val: any = raw;
        if (f.type === 'number') val = parseInt(raw) || 0;
        else if (f.type === 'textarea') {
          try { val = raw ? JSON.parse(raw) : []; } catch { val = raw.split(',').map(s => s.trim()).filter(Boolean); }
        } else if (raw && raw.includes(',')) {
          val = raw.split(',').map(s => s.trim()).filter(Boolean);
        }
        payload[f.key] = val;
      });

      if (editing) {
        await config.update(editing.id, payload);
        success('Updated', `${config.label.slice(0, -1)} updated successfully`);
      } else {
        delete payload.id;
        await config.create(payload);
        success('Created', `${config.label.slice(0, -1)} created successfully`);
      }
      closeModal();
      load();
    } catch (e: any) {
      error('Operation Failed', e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm(`Delete this ${config.label.slice(0, -1)}?`)) return;
    try {
      await config.remove(id);
      success('Deleted');
      load();
    } catch (e: any) {
      error('Delete Failed', e.message);
    }
  };

  return (
    <div>
      <div className="topbar">
        <div>
          <h1>{config.label}</h1>
          <div className="topbar-sub">Manage {config.label.toLowerCase()} records</div>
        </div>
        <button className="btn primary" onClick={openCreate}>+ Add {config.label.slice(0, -1)}</button>
      </div>

      <div className="glass panel table-wrap">
        <table>
          <thead>
            <tr>
              {type === 'departments' && <th>Code</th>}
              <th>Name</th>
              {type === 'rooms' && <> <th>Building</th> <th>Capacity</th> <th>Equipment</th> <th>Department</th> </>}
              {type === 'faculty' && <> <th>Email</th> <th>Max Hrs</th> <th>Qualifications</th> <th>Department</th> </>}
              {type === 'subjects' && <> <th>Code</th> <th>Equipment</th> <th>Min Cap</th> <th>Qualified Faculty</th> <th>Department</th> </>}
              {type === 'sections' && <> <th>Students</th> <th>Department</th> <th>Requirements</th> </>}
              <th>ID</th>
              <th style={{width: '80px', textAlign: 'center'}}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {items.map(item => (
              <tr key={item.id}>
                {config.renderRow(item)}
                <td className="mono">{shortId(item.id)}</td>
                <td style={{textAlign: 'center'}}>
                  <div className="row-actions">
                    <button className="btn ghost sm" onClick={() => openEdit(item)} title="Edit">✎</button>
                    <button className="btn ghost sm danger" onClick={() => handleDelete(item.id)} title="Delete">✕</button>
                  </div>
                </td>
              </tr>
            ))}
            {items.length === 0 && (
              <tr><td colSpan={99} className="empty">No {config.label.toLowerCase()} yet. Click Add to create one.</td></tr>
            )}
          </tbody>
        </table>
      </div>

      {modalOpen && (
        <div className="modal-backdrop" onClick={closeModal} role="dialog" aria-modal="true" aria-labelledby="modal-title">
          <div className="modal glass" onClick={e => e.stopPropagation()}>
            <h2 id="modal-title">{editing ? 'Edit' : 'Create'} {config.label.slice(0, -1)}</h2>
            <form onSubmit={handleSubmit}>
              <div className="form-grid">
                {config.fields.filter(f => f.key !== 'id' || !editing).map(f => (
                  <div key={f.key} className={f.type === 'textarea' ? 'full' : ''}>
                    <label htmlFor={f.key} className="field">
                      {f.label}
                      <input
                        id={f.key}
                        type={f.type === 'textarea' ? 'text' : f.type}
                        value={formData[f.key] || ''}
                        onChange={e => setFormData(prev => ({ ...prev, [f.key]: e.target.value }))}
                        disabled={f.key === 'id' && editing}
                        placeholder={f.type === 'textarea' ? 'JSON array or comma-separated' : ''}
                      />
                    </label>
                  </div>
                ))}
              </div>
              <div className="modal-actions">
                <button type="button" className="btn ghost" onClick={closeModal}>Cancel</button>
                <button type="submit" className="btn primary" disabled={loading}>
                  {loading ? 'Saving...' : editing ? 'Save Changes' : 'Create'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}