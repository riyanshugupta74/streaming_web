import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  useShow, useUpdateShow, useDeleteShow,
  useCreateSeason, useDeleteSeason,
  useCreateEpisode, useUpdateEpisode, useDeleteEpisode,
  useUploadArtwork, useDeleteArtwork,
} from '../hooks';
import type { Show, Season, Episode, Artwork } from '../types';
import ArtworkUpload from '../components/ArtworkUpload';

const CATEGORIES = ['Kids', 'Adventure', 'Documentary', 'Drama', 'Comedy'];
const SECTIONS = ['Featured', 'Kids', 'Adventure', 'Documentary'];
const LANGUAGES = ['English', 'Hindi', 'Tamil'];

export default function ShowDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: show, isLoading, isError, error } = useShow(id!);
  const updateShowMutation = useUpdateShow();
  const deleteShowMutation = useDeleteShow();
  const createSeasonMutation = useCreateSeason();
  const deleteSeasonMutation = useDeleteSeason();
  const createEpisodeMutation = useCreateEpisode();
  const updateEpisodeMutation = useUpdateEpisode();
  const deleteEpisodeMutation = useDeleteEpisode();

  const [editingShow, setEditingShow] = useState(false);
  const [showForm, setShowForm] = useState<Record<string, string>>({});
  const [newSeason, setNewSeason] = useState({ number: '', title: '' });
  const [showSeasonForm, setShowSeasonForm] = useState(false);
  const [newEpisodeSeasonId, setNewEpisodeSeasonId] = useState<string | null>(null);
  const [episodeForm, setEpisodeForm] = useState({
    episode_number: '', title: '', description: '', duration: '',
    content_group: '', language: 'English', status: 'draft',
  });

  if (isLoading) return <div className="text-center py-12 text-gray-500 animate-pulse">Loading show...</div>;
  if (isError) return (
    <div className="p-4 bg-red-50 border border-red-200 text-red-700 rounded-md">
      {(error as any)?.response?.status === 404
        ? 'Show not found.'
        : `Error: ${(error as any)?.message}`}
    </div>
  );
  if (!show) return null;

  const startEditing = () => {
    setShowForm({
      title: show.title, synopsis: show.synopsis || '',
      category: show.category, section: show.section || '', status: show.status,
    });
    setEditingShow(true);
  };

  const saveShow = async () => {
    await updateShowMutation.mutateAsync({ id: show.id, data: showForm });
    setEditingShow(false);
  };

  const deleteShow = async () => {
    if (confirm(`Delete "${show.title}"? This cannot be undone.`)) {
      await deleteShowMutation.mutateAsync(show.id);
      navigate('/shows');
    }
  };

  const addSeason = async () => {
    await createSeasonMutation.mutateAsync({
      showId: show.id,
      data: { season_number: parseInt(newSeason.number), title: newSeason.title },
    });
    setNewSeason({ number: '', title: '' });
    setShowSeasonForm(false);
  };

  const addEpisode = async () => {
    if (!newEpisodeSeasonId) return;
    const data = {
      episode_number: parseInt(episodeForm.episode_number),
      title: episodeForm.title,
      description: episodeForm.description,
      duration: episodeForm.duration ? parseInt(episodeForm.duration) : null,
      content_group: episodeForm.content_group,
      language: episodeForm.language,
      status: episodeForm.status,
    };
    await createEpisodeMutation.mutateAsync({ seasonId: newEpisodeSeasonId, data });
    setNewEpisodeSeasonId(null);
    setEpisodeForm({
      episode_number: '', title: '', description: '', duration: '',
      content_group: '', language: 'English', status: 'draft',
    });
  };

  const apiBase = import.meta.env.VITE_API_URL || '/api';

  return (
    <div className="space-y-6">
      {/* Show Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{show.title}</h1>
          <div className="flex gap-2 mt-2">
            <span className="px-2 py-1 bg-gray-100 rounded text-xs text-gray-600">{show.category}</span>
            {show.section && <span className="px-2 py-1 bg-blue-50 rounded text-xs text-blue-600">{show.section}</span>}
            <span className={`px-2 py-1 rounded text-xs font-medium ${
              show.status === 'published' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'
            }`}>{show.status}</span>
          </div>
        </div>
        <div className="flex gap-2">
          <button onClick={startEditing} className="px-3 py-1.5 text-sm border border-gray-300 rounded-md hover:bg-gray-50">
            Edit
          </button>
          <button onClick={deleteShow} className="px-3 py-1.5 text-sm text-red-600 border border-red-200 rounded-md hover:bg-red-50">
            Delete
          </button>
        </div>
      </div>

      {/* Edit Show Modal */}
      {editingShow && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold mb-4">Edit Show</h2>
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
              <input value={showForm.title} onChange={e => setShowForm({...showForm, title: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-indigo-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Synopsis</label>
              <textarea value={showForm.synopsis} onChange={e => setShowForm({...showForm, synopsis: e.target.value})}
                rows={3} className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-indigo-500" />
            </div>
            <div className="grid grid-cols-3 gap-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
                <select value={showForm.category} onChange={e => setShowForm({...showForm, category: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm">
                  {CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Section</label>
                <select value={showForm.section} onChange={e => setShowForm({...showForm, section: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm">
                  <option value="">— None —</option>
                  {SECTIONS.map(s => <option key={s} value={s}>{s}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
                <select value={showForm.status} onChange={e => setShowForm({...showForm, status: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm">
                  <option value="draft">Draft</option>
                  <option value="published">Published</option>
                </select>
              </div>
            </div>
            <div className="flex gap-2 pt-2">
              <button onClick={saveShow} disabled={updateShowMutation.isPending}
                className="px-4 py-2 bg-indigo-600 text-white rounded-md text-sm hover:bg-indigo-700 disabled:opacity-50">
                {updateShowMutation.isPending ? 'Saving...' : 'Save'}
              </button>
              <button onClick={() => setEditingShow(false)}
                className="px-4 py-2 border border-gray-300 rounded-md text-sm hover:bg-gray-50">Cancel</button>
            </div>
          </div>
        </div>
      )}

      {/* Show Artwork */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold mb-4">Show Artwork</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <ArtworkUpload
            label="Poster"
            type="poster"
            showId={show.id}
            existing={show.artwork.find(a => a.type === 'poster')}
            specs="2:3 ratio, ~600×900, max 200 KB"
            apiBase={apiBase}
          />
          <ArtworkUpload
            label="Banner"
            type="banner"
            showId={show.id}
            existing={show.artwork.find(a => a.type === 'banner')}
            specs="16:9 ratio, ~1280×720, max 200 KB"
            apiBase={apiBase}
          />
          <ArtworkUpload
            label="Thumbnail"
            type="thumbnail"
            showId={show.id}
            existing={show.artwork.find(a => a.type === 'thumbnail')}
            specs="16:9 ratio, ~640×360, max 200 KB"
            apiBase={apiBase}
          />
        </div>
      </div>

      {/* Seasons & Episodes */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold">Seasons & Episodes</h2>
          <button onClick={() => setShowSeasonForm(true)}
            className="px-3 py-1.5 text-sm bg-indigo-600 text-white rounded-md hover:bg-indigo-700">
            + Add Season
          </button>
        </div>

        {showSeasonForm && (
          <div className="p-4 mb-4 bg-gray-50 rounded-lg border border-gray-200">
            <h3 className="text-sm font-medium mb-2">New Season</h3>
            <div className="grid grid-cols-2 gap-3">
              <input placeholder="Season number" type="number" value={newSeason.number}
                onChange={e => setNewSeason({...newSeason, number: e.target.value})}
                className="px-3 py-2 border border-gray-300 rounded-md text-sm" />
              <input placeholder="Season title" value={newSeason.title}
                onChange={e => setNewSeason({...newSeason, title: e.target.value})}
                className="px-3 py-2 border border-gray-300 rounded-md text-sm" />
            </div>
            <div className="flex gap-2 mt-2">
              <button onClick={addSeason} disabled={!newSeason.number || !newSeason.title}
                className="px-3 py-1.5 bg-indigo-600 text-white rounded text-sm disabled:opacity-50">Create</button>
              <button onClick={() => setShowSeasonForm(false)}
                className="px-3 py-1.5 border border-gray-300 rounded text-sm">Cancel</button>
            </div>
          </div>
        )}

        {show.seasons.length === 0 && (
          <p className="text-gray-500 text-sm py-4">No seasons yet. Add a season to start adding episodes.</p>
        )}

        {show.seasons.map((season) => (
          <div key={season.id} className="mb-6 last:mb-0">
            <div className="flex justify-between items-center mb-2">
              <h3 className="font-medium text-gray-800">
                Season {season.season_number}: {season.title}
                {season.season_number === 0 && (
                  <span className="ml-2 text-xs bg-orange-100 text-orange-600 px-2 py-0.5 rounded">Trailers</span>
                )}
              </h3>
              <div className="flex gap-2">
                <button onClick={() => setNewEpisodeSeasonId(season.id)}
                  className="text-sm text-indigo-600 hover:text-indigo-800">+ Episode</button>
                <button onClick={() => {
                  if (confirm(`Delete Season ${season.season_number}?`)) deleteSeasonMutation.mutate(season.id);
                }} className="text-sm text-red-500 hover:text-red-700">Delete</button>
              </div>
            </div>

            {/* New Episode Form */}
            {newEpisodeSeasonId === season.id && (
              <div className="p-4 mb-3 bg-blue-50 rounded-lg border border-blue-200">
                <h4 className="text-sm font-medium mb-2">New Episode</h4>
                <div className="grid grid-cols-2 gap-3 mb-2">
                  <input placeholder="Episode #" type="number" value={episodeForm.episode_number}
                    onChange={e => setEpisodeForm({...episodeForm, episode_number: e.target.value})}
                    className="px-3 py-2 border border-gray-300 rounded-md text-sm" />
                  <input placeholder="Title" value={episodeForm.title}
                    onChange={e => setEpisodeForm({...episodeForm, title: e.target.value})}
                    className="px-3 py-2 border border-gray-300 rounded-md text-sm" />
                  <input placeholder="Content group" value={episodeForm.content_group}
                    onChange={e => setEpisodeForm({...episodeForm, content_group: e.target.value})}
                    className="px-3 py-2 border border-gray-300 rounded-md text-sm" />
                  <input placeholder="Duration (seconds)" type="number" value={episodeForm.duration}
                    onChange={e => setEpisodeForm({...episodeForm, duration: e.target.value})}
                    className="px-3 py-2 border border-gray-300 rounded-md text-sm" />
                  <select value={episodeForm.language}
                    onChange={e => setEpisodeForm({...episodeForm, language: e.target.value})}
                    className="px-3 py-2 border border-gray-300 rounded-md text-sm">
                    {LANGUAGES.map(l => <option key={l} value={l}>{l}</option>)}
                  </select>
                  <select value={episodeForm.status}
                    onChange={e => setEpisodeForm({...episodeForm, status: e.target.value})}
                    className="px-3 py-2 border border-gray-300 rounded-md text-sm">
                    <option value="draft">Draft</option>
                    <option value="published">Published</option>
                  </select>
                </div>
                <textarea placeholder="Description" value={episodeForm.description}
                  onChange={e => setEpisodeForm({...episodeForm, description: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm mb-2" rows={2} />
                <div className="flex gap-2">
                  <button onClick={addEpisode}
                    className="px-3 py-1.5 bg-indigo-600 text-white rounded text-sm">Create</button>
                  <button onClick={() => setNewEpisodeSeasonId(null)}
                    className="px-3 py-1.5 border border-gray-300 rounded text-sm">Cancel</button>
                </div>
              </div>
            )}

            {/* Episode List */}
            {season.episodes.length === 0 ? (
              <p className="text-gray-400 text-sm pl-4">No episodes</p>
            ) : (
              <div className="border border-gray-200 rounded-md overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200 text-sm">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">#</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Title</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Language</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Content Group</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Duration</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Status</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Art</th>
                      <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {season.episodes.map((ep) => (
                      <EpisodeRow key={ep.id} episode={ep} showId={show.id} apiBase={apiBase} />
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

// ─── Episode Row Component ─────────────────────────────────────────────────

function EpisodeRow({ episode, showId, apiBase }: { episode: Episode; showId: string; apiBase: string }) {
  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState({
    duration: episode.duration?.toString() || '',
    status: episode.status,
    description: episode.description || '',
  });
  const updateMutation = useUpdateEpisode();
  const deleteMutation = useDeleteEpisode();

  const save = async () => {
    await updateMutation.mutateAsync({
      id: episode.id,
      data: {
        duration: form.duration ? parseInt(form.duration) : null,
        status: form.status,
        description: form.description,
      },
    });
    setEditing(false);
  };

  const formatDuration = (seconds: number | null) => {
    if (!seconds) return '—';
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}:${s.toString().padStart(2, '0')}`;
  };

  return (
    <>
      <tr className="hover:bg-gray-50">
        <td className="px-4 py-2 font-medium">{episode.episode_number}</td>
        <td className="px-4 py-2">{episode.title}</td>
        <td className="px-4 py-2 text-gray-500">{episode.language}</td>
        <td className="px-4 py-2 text-gray-400 text-xs font-mono">{episode.content_group}</td>
        <td className="px-4 py-2">
          {episode.duration ? formatDuration(episode.duration) :
            <span className="text-red-500 text-xs">Missing</span>}
        </td>
        <td className="px-4 py-2">
          <span className={`px-1.5 py-0.5 rounded text-xs ${
            episode.status === 'published' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'
          }`}>{episode.status}</span>
        </td>
        <td className="px-4 py-2">
          {episode.artwork.length > 0 ?
            <span className="text-green-500 text-xs">✓ {episode.artwork.length}</span> :
            <span className="text-gray-400 text-xs">—</span>}
        </td>
        <td className="px-4 py-2 text-right">
          <button onClick={() => setEditing(!editing)} className="text-indigo-600 hover:text-indigo-800 text-xs mr-2">
            Edit
          </button>
          <button onClick={() => {
            if (confirm(`Delete episode "${episode.title}"?`)) deleteMutation.mutate(episode.id);
          }} className="text-red-500 hover:text-red-700 text-xs">
            Delete
          </button>
        </td>
      </tr>
      {editing && (
        <tr>
          <td colSpan={8} className="px-4 py-3 bg-blue-50">
            <div className="grid grid-cols-3 gap-3 mb-2">
              <div>
                <label className="text-xs font-medium text-gray-600">Duration (seconds)</label>
                <input type="number" value={form.duration}
                  onChange={e => setForm({...form, duration: e.target.value})}
                  className="w-full mt-1 px-2 py-1.5 border border-gray-300 rounded text-sm" />
              </div>
              <div>
                <label className="text-xs font-medium text-gray-600">Status</label>
                <select value={form.status} onChange={e => setForm({...form, status: e.target.value})}
                  className="w-full mt-1 px-2 py-1.5 border border-gray-300 rounded text-sm">
                  <option value="draft">Draft</option>
                  <option value="published">Published</option>
                </select>
              </div>
              <div>
                <label className="text-xs font-medium text-gray-600">Description</label>
                <input value={form.description} onChange={e => setForm({...form, description: e.target.value})}
                  className="w-full mt-1 px-2 py-1.5 border border-gray-300 rounded text-sm" />
              </div>
            </div>
            <div className="mb-3">
              <label className="text-xs font-medium text-gray-600 block mb-1">Episode Thumbnail</label>
              <ArtworkUpload
                label="Thumbnail"
                type="thumbnail"
                episodeId={episode.id}
                existing={episode.artwork.find(a => a.type === 'thumbnail')}
                specs="16:9 ratio, ~640×360, max 200 KB"
                apiBase={apiBase}
                compact
              />
            </div>
            <div className="flex gap-2">
              <button onClick={save} disabled={updateMutation.isPending}
                className="px-3 py-1 bg-indigo-600 text-white rounded text-sm disabled:opacity-50">Save</button>
              <button onClick={() => setEditing(false)}
                className="px-3 py-1 border border-gray-300 rounded text-sm">Cancel</button>
            </div>
          </td>
        </tr>
      )}
    </>
  );
}
