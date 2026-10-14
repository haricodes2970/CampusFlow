import { useState, useCallback } from 'react';

export interface Toast {
  id: number;
  type: 'success' | 'error' | 'info';
  title: string;
  message?: string;
  details?: string[];
}

let nextId = 0;

export function useToast() {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const add = useCallback((toast: Omit<Toast, 'id'>) => {
    const id = ++nextId;
    setToasts(prev => [...prev, { ...toast, id }]);
    if (toast.type !== 'error') {
      setTimeout(() => remove(id), 4500);
    }
  }, []);

  const success = useCallback((title: string, message?: string) => add({ type: 'success', title, message }), [add]);
  const error = useCallback((title: string, message?: string, details?: string[]) => add({ type: 'error', title, message, details }), [add]);
  const info = useCallback((title: string, message?: string) => add({ type: 'info', title, message }), [add]);

  const remove = useCallback((id: number) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  }, []);

  return { toasts, success, error, info, remove };
}

export function ToastContainer({ toasts, onRemove }: { toasts: Toast[]; onRemove: (id: number) => void }) {
  if (!toasts.length) return null;

  return (
    <div className="toast-wrap" role="region" aria-live="polite" aria-label="Notifications">
      {toasts.map(t => (
        <div key={t.id} className={`toast ${t.type === 'error' ? 'error' : t.type === 'success' ? 'success' : ''}`}>
          <div className="toast-title">{t.title}</div>
          {t.message && <div>{t.message}</div>}
          {t.details && t.details.length > 0 && (
            <ul>
              {t.details.map((d, i) => <li key={i}>{d}</li>)}
            </ul>
          )}
          <button className="btn ghost sm" style={{marginTop: 8}} onClick={() => onRemove(t.id)}>Dismiss</button>
        </div>
      ))}
    </div>
  );
}