import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout'
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import RuleEngine from './pages/RuleEngine';

import Entities from './pages/Entities';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const token = localStorage.getItem('token');
  if (!token) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        
        <Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="explorer" element={<Entities />} />
          <Route path="rules" element={<RuleEngine />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
