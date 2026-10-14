import { useState, useCallback } from 'react';
import { Sidebar } from './components/Sidebar';
import { DashboardView } from './components/DashboardView';
import { EntityManager } from './components/EntityManager';
import { TimetableView } from './components/TimetableView';
import { ToastContainer, useToast } from './components/Toast';

type NavKey = 'dashboard' | 'departments' | 'rooms' | 'faculty' | 'subjects' | 'sections' | 'timetable';

function App() {
  const [active, setActive] = useState<NavKey>('dashboard');
  const { toasts, success, error, info, remove } = useToast();

  const renderView = () => {
    switch (active) {
      case 'dashboard':
        return <DashboardView onNavigate={setActive} onError={error} onSuccess={success} />;
      case 'timetable':
        return <TimetableView onError={error} onSuccess={success} />;
      default:
        return <EntityManager type={active} />;
    }
  };

  return (
    <div className="app">
      <Sidebar active={active} onChange={setActive} />
      <main className="main" role="main">
        {renderView()}
      </main>
      <ToastContainer toasts={toasts} onRemove={remove} />
    </div>
  );
}

export default App;