import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useShows, useDeleteShow } from '../hooks';

const SECTIONS = ['', 'Featured', 'Kids', 'Adventure', 'Documentary'];
const STATUSES = ['', 'draft', 'published'];

export default function ShowsPage() {
  const [search, setSearch] = useState('');
  const [section, setSection] = useState('');
  const [status, setStatus] = useState('');
  const [page, setPage] = useState(1);
  const pageSize = 20;

  const { data, isLoading, isError, error } = useShows({
    page,
    page_size: pageSize,
    search: search || undefined,
    section: section || undefined,
    status: status || undefined,
  });

  const deleteMutation = useDeleteShow();

  const handleDelete = async (id: string, title: string) => {
    if (confirm(`Delete "${title}" and all its content? This cannot be undone.`)) {
      deleteMutation.mutate(id);
    }
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Shows</h1>
        <Link
          to="/shows/new"
          className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors text-sm font-medium"
        >
          + New Show
        </Link>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
          <div>
            <label className="block text-xs font-medium text-gray-500 mb-1">Search</label>
            <input
              type="text"
              value={search}
              onChange={(e) => { setSearch(e.target.value); setPage(1); }}
              placeholder="Search by title..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-500 mb-1">Section</label>
            <select
              value={section}
              onChange={(e) => { setSection(e.target.value); setPage(1); }}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="">All Sections</option>
              {SECTIONS.filter(Boolean).map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-500 mb-1">Status</label>
            <select
              value={status}
              onChange={(e) => { setStatus(e.target.value); setPage(1); }}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="">All Statuses</option>
              {STATUSES.filter(Boolean).map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* States */}
      {isLoading && (
        <div className="text-center py-12 text-gray-500">
          <div className="animate-pulse">Loading shows...</div>
        </div>
      )}

      {isError && (
        <div className="p-4 bg-red-50 border border-red-200 text-red-700 rounded-md">
          {(error as any)?.response?.status === 403
            ? 'You do not have permission to view this page.'
            : `Error loading shows: ${(error as any)?.message || 'Unknown error'}`}
        </div>
      )}

      {data && data.items.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500 text-lg">No shows found</p>
          <p className="text-gray-400 text-sm mt-1">
            {search || section || status
              ? 'Try adjusting your filters'
              : 'Create your first show to get started'}
          </p>
        </div>
      )}

      {/* Table */}
      {data && data.items.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Title</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Category</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Section</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Content</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Updated</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {data.items.map((show) => (
                <tr key={show.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <Link to={`/shows/${show.id}`} className="text-indigo-600 hover:text-indigo-800 font-medium">
                      {show.title}
                    </Link>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-600">{show.category}</td>
                  <td className="px-6 py-4 text-sm text-gray-600">{show.section || '—'}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      show.status === 'published'
                        ? 'bg-green-100 text-green-700'
                        : 'bg-yellow-100 text-yellow-700'
                    }`}>
                      {show.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {show.season_count}S / {show.episode_count}E
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {new Date(show.updated_at).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <button
                      onClick={() => handleDelete(show.id, show.title)}
                      className="text-red-500 hover:text-red-700 text-sm"
                      disabled={deleteMutation.isPending}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {/* Pagination */}
          {data.total_pages > 1 && (
            <div className="px-6 py-3 bg-gray-50 border-t border-gray-200 flex items-center justify-between">
              <p className="text-sm text-gray-500">
                Page {data.page} of {data.total_pages} ({data.total} total)
              </p>
              <div className="flex gap-2">
                <button
                  onClick={() => setPage(p => Math.max(1, p - 1))}
                  disabled={page <= 1}
                  className="px-3 py-1 border border-gray-300 rounded text-sm disabled:opacity-50 hover:bg-gray-100"
                >
                  Previous
                </button>
                <button
                  onClick={() => setPage(p => Math.min(data.total_pages, p + 1))}
                  disabled={page >= data.total_pages}
                  className="px-3 py-1 border border-gray-300 rounded text-sm disabled:opacity-50 hover:bg-gray-100"
                >
                  Next
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
