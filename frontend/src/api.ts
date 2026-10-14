const rawApiBase = import.meta.env.VITE_API_BASE;

// Non-secret build-time diagnostic log for debugging Vercel environment variable injection
console.log("[CampusFlow Diagnostic] BUILD_MODE:", import.meta.env.MODE);
console.log("[CampusFlow Diagnostic] PROD:", import.meta.env.PROD);
console.log("[CampusFlow Diagnostic] VITE_API_BASE present:", Boolean(rawApiBase));
if (rawApiBase) {
  try {
    const parsed = new URL(rawApiBase);
    console.log("[CampusFlow Diagnostic] VITE_API_BASE origin:", parsed.origin);
    console.log("[CampusFlow Diagnostic] VITE_API_BASE pathname:", parsed.pathname);
  } catch {
    console.log("[CampusFlow Diagnostic] VITE_API_BASE is a relative or custom path string length:", rawApiBase.length);
  }
} else if (import.meta.env.PROD) {
  console.error(
    "[CampusFlow Diagnostic] CRITICAL: VITE_API_BASE is missing in production build! " +
    "Please verify Vercel Project Settings → Environment Variables has VITE_API_BASE configured for Production environment and redeploy without cache."
  );
}

if (!rawApiBase && import.meta.env.PROD) {
  throw new Error(
    "CRITICAL CONFIGURATION ERROR: VITE_API_BASE environment variable is not defined in production build. " +
    "Please configure VITE_API_BASE in your Vercel project settings pointing to your Render backend API (e.g., https://campusflow-a9hq.onrender.com/api)."
  );
}

const API_BASE = rawApiBase || 'http://localhost:8000/api';

async function fetchJson<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(err.detail?.message || err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

function toQuery(params: Record<string, any>): string {
  const q = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => v !== undefined && q.append(k, String(v)));
  return q.toString() ? `?${q}` : '';
}

export const api = {
  // Health
  health: () => fetchJson<{ status: string }>('/health'),

  // Stats
  stats: () => fetchJson<{
    departments: number;
    rooms: number;
    faculty: number;
    subjects: number;
    sections: number;
    scheduled_sessions: number;
    unscheduled_sessions: number;
    unscheduled_details: number;
  }>('/stats'),

  // Departments
  listDepartments: () => fetchJson<any[]>('/departments'),
  createDepartment: (d: any) => fetchJson<any>('/departments', { method: 'POST', body: JSON.stringify(d) }),
  updateDepartment: (id: string, d: any) => fetchJson<any>(`/departments/${id}`, { method: 'PUT', body: JSON.stringify(d) }),
  deleteDepartment: (id: string) => fetchJson<any>(`/departments/${id}`, { method: 'DELETE' }),

  // Rooms
  listRooms: () => fetchJson<any[]>('/rooms'),
  createRoom: (r: any) => fetchJson<any>('/rooms', { method: 'POST', body: JSON.stringify(r) }),
  updateRoom: (id: string, r: any) => fetchJson<any>(`/rooms/${id}`, { method: 'PUT', body: JSON.stringify(r) }),
  deleteRoom: (id: string) => fetchJson<any>(`/rooms/${id}`, { method: 'DELETE' }),

  // Faculty
  listFaculty: () => fetchJson<any[]>('/faculty'),
  createFaculty: (f: any) => fetchJson<any>('/faculty', { method: 'POST', body: JSON.stringify(f) }),
  updateFaculty: (id: string, f: any) => fetchJson<any>(`/faculty/${id}`, { method: 'PUT', body: JSON.stringify(f) }),
  deleteFaculty: (id: string) => fetchJson<any>(`/faculty/${id}`, { method: 'DELETE' }),

  // Subjects
  listSubjects: () => fetchJson<any[]>('/subjects'),
  createSubject: (s: any) => fetchJson<any>('/subjects', { method: 'POST', body: JSON.stringify(s) }),
  updateSubject: (id: string, s: any) => fetchJson<any>(`/subjects/${id}`, { method: 'PUT', body: JSON.stringify(s) }),
  deleteSubject: (id: string) => fetchJson<any>(`/subjects/${id}`, { method: 'DELETE' }),

  // Sections
  listSections: () => fetchJson<any[]>('/sections'),
  createSection: (s: any) => fetchJson<any>('/sections', { method: 'POST', body: JSON.stringify(s) }),
  updateSection: (id: string, s: any) => fetchJson<any>(`/sections/${id}`, { method: 'PUT', body: JSON.stringify(s) }),
  deleteSection: (id: string) => fetchJson<any>(`/sections/${id}`, { method: 'DELETE' }),

  // Timetable
  generate: () => fetchJson<any>('/timetable/generate', { method: 'POST' }),
  getTimetable: () => fetchJson<any>('/timetable'),
  getUnscheduled: () => fetchJson<any[]>('/timetable/unscheduled'),

  // Sessions
  listSessions: () => fetchJson<any[]>('/sessions'),
  createSession: (s: any) => fetchJson<any>('/sessions', { method: 'POST', body: JSON.stringify(s) }),
  updateSession: (id: string, s: any) => fetchJson<any>(`/sessions/${id}`, { method: 'PUT', body: JSON.stringify(s) }),
  deleteSession: (id: string) => fetchJson<any>(`/sessions/${id}`, { method: 'DELETE' }),
};