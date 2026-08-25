import { Outlet, Link, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks';

export default function Layout() {
  const { user, isAdmin, logout } = useAuth();
  const location = useLocation();

  const navItems = [
    { path: '/shows', label: 'Shows' },
    { path: '/publish', label: 'Publish' },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-8">
              <Link to="/shows" className="text-xl font-bold text-indigo-600">
                Peblo TV CMS
              </Link>
              <nav className="flex gap-1">
                {navItems.map((item) => (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                      location.pathname.startsWith(item.path)
                        ? 'bg-indigo-50 text-indigo-700'
                        : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                    }`}
                  >
                    {item.label}
                  </Link>
                ))}
              </nav>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-sm text-gray-600">
                {user?.email}
                <span className={`ml-2 px-2 py-0.5 rounded-full text-xs font-medium ${
                  isAdmin()
                    ? 'bg-purple-100 text-purple-700'
                    : 'bg-blue-100 text-blue-700'
                }`}>
                  {user?.role}
                </span>
              </div>
              <button
                onClick={logout}
                className="text-sm text-gray-500 hover:text-gray-700 transition-colors"
              >
                Sign Out
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Outlet />
      </main>
    </div>
  );
}
