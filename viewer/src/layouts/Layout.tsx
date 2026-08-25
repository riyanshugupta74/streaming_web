import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { useAuth } from '../AuthContext';

export default function Layout() {
  const [searchQuery, setSearchQuery] = useState('');
  const [isScrolled, setIsScrolled] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 0);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-[#141414] text-gray-100 flex flex-col font-sans">
      {/* Navigation */}
      <header
        className={`fixed w-full top-0 z-50 transition-colors duration-300 ${
          isScrolled ? 'bg-[#141414]' : 'bg-transparent bg-gradient-to-b from-black/80 to-transparent'
        }`}
      >
        <div className="px-4 sm:px-6 lg:px-12">
          <div className="flex justify-between items-center h-16">
            <Link to="/" className="text-3xl font-bold text-[#E50914] tracking-tighter">
              PEBLO TV
            </Link>

            <div className="flex items-center space-x-6">
              <form onSubmit={handleSearch} className="flex-1 max-w-xs mx-4 lg:max-w-sm ml-auto flex justify-end">
                <div className="relative group">
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search movies & shows..."
                    className="w-0 opacity-0 group-hover:w-full group-hover:opacity-100 focus:w-full focus:opacity-100 transition-all duration-300 bg-black/60 border border-white/80 rounded-sm py-1.5 pl-4 pr-10 text-sm focus:outline-none placeholder-gray-400 text-white"
                  />
                  <button
                    type="submit"
                    className="absolute right-0 top-0 mt-1.5 mr-3 text-white focus:outline-none"
                    aria-label="Search"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                    </svg>
                  </button>
                </div>
              </form>

              {user ? (
                <div className="flex items-center space-x-4">
                  <span className="text-sm font-medium hidden sm:block">{user.email}</span>
                  <button 
                    onClick={handleLogout}
                    className="text-sm bg-zinc-800 hover:bg-zinc-700 px-3 py-1.5 rounded transition"
                  >
                    Sign Out
                  </button>
                </div>
              ) : (
                <Link 
                  to="/login"
                  className="bg-red-600 hover:bg-red-700 text-white text-sm font-medium px-4 py-1.5 rounded transition"
                >
                  Sign In
                </Link>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 w-full pb-12">
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="bg-[#141414] mt-12 py-8 text-center text-gray-500 text-sm">
        <p>Peblo TV Mini. A technical challenge implementation.</p>
      </footer>
    </div>
  );
}
