import { useState, FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCreateShow } from '../hooks';

const CATEGORIES = ['Kids', 'Adventure', 'Documentary', 'Drama', 'Comedy'];
const SECTIONS = ['Featured', 'Kids', 'Adventure', 'Documentary'];

export default function ShowCreatePage() {
  const [title, setTitle] = useState('');
  const [synopsis, setSynopsis] = useState('');
  const [category, setCategory] = useState('Kids');
  const [section, setSection] = useState('');
  const [status, setStatus] = useState('draft');
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const createMutation = useCreateShow();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');

    try {
      const res = await createMutation.mutateAsync({
        title, synopsis, category, section, status,
      });
      navigate(`/shows/${res.data.id}`);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create show');
    }
  };

  return (
    <div className="max-w-2xl">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Create New Show</h1>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div className="p-3 bg-red-50 border border-red-200 text-red-700 rounded-md text-sm">{error}</div>
          )}

          <div>
            <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
              Title <span className="text-red-500">*</span>
            </label>
            <input
              id="title"
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
              required
            />
          </div>

          <div>
            <label htmlFor="synopsis" className="block text-sm font-medium text-gray-700 mb-1">Synopsis</label>
            <textarea
              id="synopsis"
              value={synopsis}
              onChange={(e) => setSynopsis(e.target.value)}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label htmlFor="category" className="block text-sm font-medium text-gray-700 mb-1">
                Category <span className="text-red-500">*</span>
              </label>
              <select
                id="category"
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                {CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>

            <div>
              <label htmlFor="section" className="block text-sm font-medium text-gray-700 mb-1">Section</label>
              <select
                id="section"
                value={section}
                onChange={(e) => setSection(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="">— None —</option>
                {SECTIONS.map((s) => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>
          </div>

          <div>
            <label htmlFor="status" className="block text-sm font-medium text-gray-700 mb-1">Status</label>
            <select
              id="status"
              value={status}
              onChange={(e) => setStatus(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="draft">Draft</option>
              <option value="published">Published</option>
            </select>
          </div>

          <div className="flex gap-3 pt-4">
            <button
              type="submit"
              disabled={createMutation.isPending}
              className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50 transition-colors font-medium"
            >
              {createMutation.isPending ? 'Creating...' : 'Create Show'}
            </button>
            <button
              type="button"
              onClick={() => navigate('/shows')}
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
