export const DAYS: Array<'MONDAY' | 'TUESDAY' | 'WEDNESDAY' | 'THURSDAY' | 'FRIDAY' | 'SATURDAY' | 'SUNDAY'> = [
  'MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY'
];

export const DAY_LABELS: Record<string, string> = {
  MONDAY: 'Mon', TUESDAY: 'Tue', WEDNESDAY: 'Wed',
  THURSDAY: 'Thu', FRIDAY: 'Fri', SATURDAY: 'Sat', SUNDAY: 'Sun'
};

export const SLOT_DURATION = 30;
export const SLOTS_PER_DAY = 24;
export const VISIBLE_START_SLOT = 14; // 07:00
export const VISIBLE_END_SLOT = 38; // 19:00

export function timeToSlot(time: string): number {
  const [h, m] = time.split(':').map(Number);
  return h * 2 + Math.floor(m / 30);
}

export function slotToTime(slot: number): string {
  const h = Math.floor(slot / 2);
  const m = (slot % 2) * 30;
  return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}`;
}

export function formatSlotRange(startSlot: number, durationSlots: number): string {
  return `${slotToTime(startSlot)} – ${slotToTime(startSlot + durationSlots)}`;
}

export function getSessionColor(subjectId: string): string {
  // Deterministic color from subject ID
  let hash = 0;
  for (let i = 0; i < subjectId.length; i++) hash = subjectId.charCodeAt(i) + ((hash << 5) - hash);
  const hues = [262, 187, 15, 330, 210, 45, 280, 12];
  return `hsl(${hues[Math.abs(hash) % hues.length]}, 72%, 48%)`;
}

export function shortId(id: string): string {
  return id.slice(0, 8);
}

export function getSubjectCode(subjects: any[], id: string): string {
  return subjects.find(s => s.id === id)?.code || id.slice(0, 6);
}

export function getFacultyName(faculty: any[], id: string): string {
  return faculty.find(f => f.id === id)?.name || id.slice(0, 6);
}

export function getRoomName(rooms: any[], id: string): string {
  return rooms.find(r => r.id === id)?.name || id.slice(0, 6);
}

export function getSectionName(sections: any[], id: string): string {
  return sections.find(s => s.id === id)?.name || id.slice(0, 6);
}

export function getDayName(day: string): string {
  return DAY_LABELS[day] || day;
}

export function isSessionOverlapping(a: any, b: any): boolean {
  if (a.day !== b.day) return false;
  const aEnd = a.start_slot + a.duration_slots;
  const bEnd = b.start_slot + b.duration_slots;
  return !(a.start_slot >= bEnd || b.start_slot >= aEnd);
}