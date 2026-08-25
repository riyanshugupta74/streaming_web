import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './hooks';
import Layout from './layouts/Layout';
import LoginPage from './pages/LoginPage';
import ShowsPage from './pages/ShowsPage';
import ShowDetailPage from './pages/ShowDetailPage';
import ShowCreatePage from './pages/ShowCreatePage';
import PublishPage from './pages/PublishPage';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuth();
  if (!isAuthenticated()) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to="/shows" replace />} />
        <Route path="shows" element={<ShowsPage />} />
        <Route path="shows/new" element={<ShowCreatePage />} />
        <Route path="shows/:id" element={<ShowDetailPage />} />
        <Route path="publish" element={<PublishPage />} />
      </Route>
    </Routes>
  );
}
