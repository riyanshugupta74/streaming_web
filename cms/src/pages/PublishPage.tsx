import { useAuth, useValidationReport, usePublish, usePublishRuns } from '../hooks';
import type { ValidationError, PublishRun } from '../types';

export default function PublishPage() {
  const { isAdmin } = useAuth();
  const { data: report, isLoading: reportLoading, isError: reportError } = useValidationReport();
  const { data: runs, isLoading: runsLoading } = usePublishRuns();
  const publishMutation = usePublish();

  const canPublish = isAdmin() && report && !report.blocking;

  const handlePublish = async () => {
    if (!confirm('Publish the catalogue? This will make the content live.')) return;
    publishMutation.mutate(undefined);
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Publish Catalogue</h1>

      {/* Permission Warning */}
      {!isAdmin() && (
        <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <p className="text-yellow-800 font-medium">⚠ Permission Required</p>
          <p className="text-yellow-700 text-sm mt-1">
            Only administrators can publish the catalogue. You can view the validation report below.
            Contact an admin to publish.
          </p>
        </div>
      )}

      {/* Publish Result */}
      {publishMutation.isSuccess && (
        <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
          <p className="text-green-800 font-medium">✓ Catalogue Published</p>
          <p className="text-green-700 text-sm mt-1">
            {(publishMutation.data as any)?.data?.message || 'Published successfully'}
          </p>
        </div>
      )}
      {publishMutation.isError && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-800 font-medium">✗ Publish Failed</p>
          <p className="text-red-700 text-sm mt-1">
            {(publishMutation.error as any)?.response?.data?.detail || 'An error occurred'}
          </p>
        </div>
      )}

      {/* Validation Report */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold mb-4">Validation Report</h2>

        {reportLoading && <p className="text-gray-500 animate-pulse">Loading validation report...</p>}
        {reportError && <p className="text-red-500">Failed to load validation report.</p>}

        {report && (
          <>
            {report.total_errors === 0 ? (
              <div className="p-4 bg-green-50 border border-green-200 rounded-lg mb-4">
                <p className="text-green-700 font-medium">✓ No validation errors</p>
                <p className="text-green-600 text-sm">All content is ready to publish.</p>
              </div>
            ) : (
              <div className="p-4 bg-red-50 border border-red-200 rounded-lg mb-4">
                <p className="text-red-700 font-medium">
                  {report.blocking ? '✗' : '⚠'} {report.total_errors} validation {report.total_errors === 1 ? 'issue' : 'issues'}
                  {report.blocking && ' (blocking)'}
                </p>
                <p className="text-red-600 text-sm">
                  {report.blocking
                    ? 'These issues must be resolved before publishing.'
                    : 'These are warnings but will not block publishing.'}
                </p>
              </div>
            )}

            {/* Show Errors */}
            {report.shows.length > 0 && (
              <ErrorSection title="Shows" errors={report.shows} />
            )}
            {report.episodes.length > 0 && (
              <ErrorSection title="Episodes" errors={report.episodes} />
            )}
            {report.artwork.length > 0 && (
              <ErrorSection title="Artwork" errors={report.artwork} />
            )}
            {report.metadata.length > 0 && (
              <ErrorSection title="Metadata" errors={report.metadata} />
            )}
          </>
        )}

        {/* Publish Button */}
        {isAdmin() && (
          <div className="mt-6 pt-4 border-t border-gray-200">
            <button
              onClick={handlePublish}
              disabled={!canPublish || publishMutation.isPending}
              className={`px-6 py-2.5 rounded-md font-medium text-sm transition-colors ${
                canPublish
                  ? 'bg-indigo-600 text-white hover:bg-indigo-700'
                  : 'bg-gray-200 text-gray-500 cursor-not-allowed'
              }`}
            >
              {publishMutation.isPending ? 'Publishing...' : 'Publish Catalogue'}
            </button>
            {report?.blocking && (
              <p className="text-sm text-gray-500 mt-2">
                Resolve all blocking validation errors before publishing.
              </p>
            )}
          </div>
        )}
      </div>

      {/* Publish History */}
      {isAdmin() && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold mb-4">Publish History</h2>

          {runsLoading && <p className="text-gray-500 animate-pulse">Loading...</p>}

          {runs && runs.length === 0 && (
            <p className="text-gray-500 text-sm">No publish runs yet.</p>
          )}

          {runs && runs.length > 0 && (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200 text-sm">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Date</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Status</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Shows</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Episodes</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Error</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {runs.map((run: PublishRun) => (
                    <tr key={run.id}>
                      <td className="px-4 py-2 text-gray-600">
                        {new Date(run.started_at).toLocaleString()}
                      </td>
                      <td className="px-4 py-2">
                        <StatusBadge status={run.status} />
                      </td>
                      <td className="px-4 py-2 text-gray-600">{run.shows_count}</td>
                      <td className="px-4 py-2 text-gray-600">{run.episodes_count}</td>
                      <td className="px-4 py-2 text-red-500 text-xs max-w-xs truncate">
                        {run.error || '—'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function ErrorSection({ title, errors }: { title: string; errors: ValidationError[] }) {
  return (
    <div className="mb-4">
      <h3 className="font-medium text-gray-800 mb-2">{title}</h3>
      <div className="space-y-2">
        {errors.map((err, i) => (
          <div key={i} className="p-3 bg-red-50 border border-red-100 rounded-md">
            <p className="text-sm font-medium text-red-800">❌ {err.entity_name}</p>
            <p className="text-sm text-red-700 mt-0.5">
              <span className="font-medium">Problem:</span> {err.problem}
            </p>
            <p className="text-sm text-red-600 mt-0.5">
              <span className="font-medium">Fix:</span> {err.fix}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const colors: Record<string, string> = {
    success: 'bg-green-100 text-green-700',
    failed: 'bg-red-100 text-red-700',
    blocked: 'bg-yellow-100 text-yellow-700',
    running: 'bg-blue-100 text-blue-700',
  };
  return (
    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${colors[status] || 'bg-gray-100 text-gray-700'}`}>
      {status}
    </span>
  );
}
