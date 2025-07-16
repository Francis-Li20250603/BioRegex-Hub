import { Routes, Route } from 'react-router-dom';
import HomePage from './pages/HomePage';
import RulesPage from './pages/RulesPage';
import ContributePage from './pages/ContributePage';
import ValidationPage from './pages/ValidationPage';
import AdminPage from './pages/AdminPage';
import ProtectedRoute from './components/ProtectedRoute';

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/rules" element={<RulesPage />} />
      <Route path="/contribute" element={<ContributePage />} />
      <Route path="/validate" element={<ValidationPage />} />
      <Route 
        path="/admin" 
        element={
          <ProtectedRoute roles={['admin']}>
            <AdminPage />
          </ProtectedRoute>
        } 
      />
    </Routes>
  );
}
