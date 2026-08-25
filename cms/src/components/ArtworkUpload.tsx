import { useState, useRef } from 'react';
import { useUploadArtwork, useDeleteArtwork } from '../hooks';
import type { Artwork } from '../types';

interface ArtworkUploadProps {
  label: string;
  type: 'poster' | 'banner' | 'thumbnail';
  showId?: string;
  episodeId?: string;
  existing?: Artwork;
  specs: string;
  apiBase: string;
  compact?: boolean;
}

const ARTWORK_LIMITS = {
  poster: { ratio: 2/3, minW: 300, maxW: 1200, label: '2:3' },
  banner: { ratio: 16/9, minW: 640, maxW: 2560, label: '16:9' },
  thumbnail: { ratio: 16/9, minW: 320, maxW: 1280, label: '16:9' },
};

const MAX_SIZE = 200 * 1024; // 200 KB

export default function ArtworkUpload({ label, type, showId, episodeId, existing, specs, apiBase, compact }: ArtworkUploadProps) {
  const [error, setError] = useState('');
  const [uploading, setUploading] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);
  const uploadMutation = useUploadArtwork();
  const deleteMutation = useDeleteArtwork();

  const validateClientSide = (file: File): string | null => {
    if (file.size > MAX_SIZE) {
      return `File is too large (${(file.size / 1024).toFixed(1)} KB). Maximum: 200 KB.`;
    }
    return null;
  };

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setError('');

    // Client-side validation for immediate feedback
    const clientError = validateClientSide(file);
    if (clientError) {
      setError(clientError);
      return;
    }

    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('artwork_type', type);
      if (showId) formData.append('show_id', showId);
      if (episodeId) formData.append('episode_id', episodeId);

      await uploadMutation.mutateAsync(formData);
    } catch (err: any) {
      const detail = err.response?.data?.detail;
      if (typeof detail === 'object') {
        setError(detail.details || detail.message || 'Upload failed');
      } else {
        setError(detail || 'Upload failed');
      }
    } finally {
      setUploading(false);
      if (fileRef.current) fileRef.current.value = '';
    }
  };

  const handleDelete = async () => {
    if (!existing) return;
    await deleteMutation.mutateAsync(existing.id);
  };

  const imageUrl = existing ? `${apiBase}${existing.storage_key.startsWith('/') ? '' : '/storage/'}${existing.storage_key}` : null;

  if (compact) {
    return (
      <div className="flex items-center gap-3">
        {imageUrl && (
          <img src={imageUrl} alt={label} className="h-10 w-16 object-cover rounded border" />
        )}
        <div className="flex-1">
          <input ref={fileRef} type="file" accept="image/*" onChange={handleUpload}
            className="text-xs" disabled={uploading} />
          {existing && (
            <button onClick={handleDelete} className="text-red-500 text-xs ml-2">Remove</button>
          )}
        </div>
        {error && <p className="text-red-500 text-xs">{error}</p>}
      </div>
    );
  }

  return (
    <div className="border border-gray-200 rounded-lg p-4">
      <div className="flex justify-between items-start mb-2">
        <div>
          <h3 className="font-medium text-sm text-gray-800">{label}</h3>
          <p className="text-xs text-gray-500">{specs}</p>
        </div>
        {existing && (
          <span className="text-green-500 text-xs font-medium">✓ Uploaded</span>
        )}
      </div>

      {/* Preview */}
      {imageUrl ? (
        <div className="mb-3">
          <img
            src={imageUrl}
            alt={`${label} preview`}
            className="w-full h-32 object-cover rounded border border-gray-200"
          />
          <p className="text-xs text-gray-400 mt-1">
            {existing!.width}×{existing!.height} · {(existing!.size_bytes / 1024).toFixed(1)} KB
          </p>
        </div>
      ) : (
        <div className="mb-3 w-full h-32 bg-gray-100 rounded flex items-center justify-center border border-dashed border-gray-300">
          <span className="text-gray-400 text-sm">No {label.toLowerCase()}</span>
        </div>
      )}

      {/* Upload */}
      <div className="flex gap-2">
        <label className="flex-1">
          <input
            ref={fileRef}
            type="file"
            accept="image/jpeg,image/png,image/webp"
            onChange={handleUpload}
            className="hidden"
            disabled={uploading}
          />
          <span className={`block text-center px-3 py-1.5 border border-gray-300 rounded-md text-sm cursor-pointer hover:bg-gray-50 ${
            uploading ? 'opacity-50' : ''
          }`}>
            {uploading ? 'Uploading...' : existing ? 'Replace' : 'Upload'}
          </span>
        </label>
        {existing && (
          <button
            onClick={handleDelete}
            disabled={deleteMutation.isPending}
            className="px-3 py-1.5 text-sm text-red-600 border border-red-200 rounded-md hover:bg-red-50"
          >
            Remove
          </button>
        )}
      </div>

      {/* Error */}
      {error && (
        <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded text-xs text-red-700 whitespace-pre-line">
          {error}
        </div>
      )}
    </div>
  );
}
