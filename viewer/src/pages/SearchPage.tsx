import { useSearchParams, Link } from 'react-router-dom';
import { useSearch } from '../hooks';
import ImageWithFallback from '../components/ImageWithFallback';

export default function SearchPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const q = searchParams.get('q') || '';
  const category = searchParams.get('category') || '';
  const language = searchParams.get('language') || '';

  const { data, loading, error } = useSearch({
    q: q || undefined,
    category: category || undefined,
    language: language || undefined,
  });

  const updateParam = (key: string, value: string) => {
    const newParams = new URLSearchParams(searchParams);
    if (value) {
      newParams.set(key, value);
    } else {
      newParams.delete(key);
    }
    setSearchParams(newParams);
  };

  const categories = ['Kids', 'Adventure', 'Documentary', 'Drama', 'Comedy'];
  const languages = ['English', 'Hindi', 'Tamil'];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex flex-col md:flex-row gap-8 items-start">
        {/* Filters Sidebar */}
        <div className="w-full md:w-64 flex-shrink-0 space-y-6 bg-gray-900 p-6 rounded-lg border border-gray-800">
          <div>
            <h3 className="text-sm font-medium text-gray-400 uppercase tracking-wider mb-3">Filters</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Category</label>
                <div className="space-y-2">
                  <button
                    onClick={() => updateParam('category', '')}
                    className={`block w-full text-left px-3 py-1.5 rounded text-sm transition-colors ${
                      !category ? 'bg-indigo-600 text-white' : 'text-gray-400 hover:bg-gray-800 hover:text-white'
                    }`}
                  >
                    All Categories
                  </button>
                  {categories.map((c) => (
                    <button
                      key={c}
                      onClick={() => updateParam('category', c)}
                      className={`block w-full text-left px-3 py-1.5 rounded text-sm transition-colors ${
                        category === c ? 'bg-indigo-600 text-white' : 'text-gray-400 hover:bg-gray-800 hover:text-white'
                      }`}
                    >
                      {c}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Language</label>
                <div className="space-y-2">
                  <button
                    onClick={() => updateParam('language', '')}
                    className={`block w-full text-left px-3 py-1.5 rounded text-sm transition-colors ${
                      !language ? 'bg-indigo-600 text-white' : 'text-gray-400 hover:bg-gray-800 hover:text-white'
                    }`}
                  >
                    All Languages
                  </button>
                  {languages.map((l) => (
                    <button
                      key={l}
                      onClick={() => updateParam('language', l)}
                      className={`block w-full text-left px-3 py-1.5 rounded text-sm transition-colors ${
                        language === l ? 'bg-indigo-600 text-white' : 'text-gray-400 hover:bg-gray-800 hover:text-white'
                      }`}
                    >
                      {l}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Results */}
        <div className="flex-1 min-w-0 w-full">
          <h1 className="text-2xl font-bold text-white mb-2">
            {q ? `Search Results for "${q}"` : 'Browse Catalogue'}
          </h1>
          <p className="text-gray-400 text-sm mb-6">
            {data ? `${data.total_results} results found` : 'Searching...'}
          </p>

          {loading && (
            <div className="flex justify-center py-12">
              <div className="w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
            </div>
          )}

          {error && (
            <div className="p-4 bg-red-900/20 border border-red-900/50 text-red-400 rounded-lg">
              Failed to perform search. Please try again.
            </div>
          )}

          {data && data.total_results === 0 && (
            <div className="text-center py-20 bg-gray-900/50 rounded-lg border border-gray-800 border-dashed">
              <p className="text-gray-400 text-lg">No matches found.</p>
              <p className="text-gray-500 text-sm mt-2">Try adjusting your filters or search term.</p>
            </div>
          )}

          {data && data.total_results > 0 && (
            <div className="space-y-8">
              {data.sections.map((section: any) => (
                <div key={section.name}>
                  {section.name !== 'Uncategorized' && (
                    <h2 className="text-lg font-semibold text-gray-300 mb-4 pb-2 border-b border-gray-800">
                      {section.name}
                    </h2>
                  )}
                  <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
                    {section.shows.map((show: any) => (
                      <Link
                        key={show.id}
                        to={`/show/${show.id}`}
                        className="group relative rounded-md overflow-hidden bg-gray-900 transition-transform duration-300 hover:scale-105 hover:z-10 focus:outline-none focus:ring-2 focus:ring-indigo-500 block"
                      >
                        <ImageWithFallback
                          src={show.artwork?.poster}
                          type="poster"
                          title={show.title}
                          className="w-full group-hover:scale-105 transition-transform duration-300"
                        />
                        <div className="absolute inset-0 bg-gradient-to-t from-gray-950 via-gray-950/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                          <div className="absolute bottom-0 left-0 p-3 w-full">
                            <h3 className="text-sm font-bold text-white truncate">{show.title}</h3>
                            <p className="text-xs text-gray-300 mt-1">{show.category}</p>
                          </div>
                        </div>
                      </Link>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
