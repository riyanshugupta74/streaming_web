import { useParams, Link } from 'react-router-dom';
import { useState } from 'react';
import { useCatalogue } from '../hooks';
import ImageWithFallback from '../components/ImageWithFallback';
import type { CatalogueShow, CatalogueSeason, CatalogueEpisode } from '../types';

export default function ShowPage() {
  const { id } = useParams<{ id: string }>();
  const { data: catalogue, loading, error } = useCatalogue();
  const [playingVideo, setPlayingVideo] = useState(false);

  if (loading) {
    return (
      <div className="flex justify-center py-20">
        <div className="w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  if (error || !catalogue) return <div className="text-center py-20 text-red-500">Failed to load show</div>;

  // Find show in catalogue
  let show: CatalogueShow | null = null;
  for (const section of catalogue.sections) {
    const found = section.shows.find(s => s.id === id);
    if (found) {
      show = found;
      break;
    }
  }

  if (!show) return <div className="text-center py-20 text-gray-400">Show not found</div>;

  const hasTrailers = show.trailers && show.trailers.length > 0;
  const hasSeasons = show.seasons && show.seasons.length > 0;

  return (
    <div className="pb-20">
      {playingVideo && (
        <div className="fixed inset-0 z-50 bg-black flex items-center justify-center">
          <button 
            onClick={() => setPlayingVideo(false)}
            className="absolute top-6 right-6 text-white hover:text-gray-300 z-50 p-2 bg-black/50 rounded-full"
          >
            <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
          <video 
            src="https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4" 
            controls 
            autoPlay 
            className="w-full max-w-6xl max-h-screen outline-none"
          />
        </div>
      )}
      
      {/* Banner / Header */}
      <div className="relative w-full h-[60vh] min-h-[400px] bg-[#141414]">
        <ImageWithFallback
          src={show.artwork?.banner}
          type="banner"
          title={show.title}
          className="absolute inset-0 w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-[#141414] via-[#141414]/70 to-transparent" />
        <div className="absolute inset-0 bg-gradient-to-r from-[#141414] via-[#141414]/50 to-transparent" />
        
        <div className="absolute bottom-0 left-0 w-full p-6 md:p-12 mb-4">
          <div className="max-w-4xl flex flex-col md:flex-row gap-8 items-end">
            <div className="hidden md:block w-48 flex-shrink-0 rounded overflow-hidden shadow-2xl shadow-black/80">
              <ImageWithFallback src={show.artwork?.poster} type="poster" title={show.title} />
            </div>
            <div>
              <h1 className="text-4xl md:text-6xl font-black text-white mb-4 drop-shadow-xl tracking-tight">{show.title}</h1>
              <div className="flex items-center gap-4 text-sm text-gray-300 mb-6 font-bold drop-shadow-md">
                <span className="text-green-500">95% Match</span>
                <span className="px-1 border border-gray-500 text-gray-300">HD</span>
                <span>{show.category}</span>
                {hasSeasons && <span>{show.seasons.length} {show.seasons.length === 1 ? 'Season' : 'Seasons'}</span>}
              </div>
              <p className="text-white max-w-2xl text-base md:text-lg leading-relaxed mb-8 drop-shadow-lg font-medium line-clamp-4">
                {show.synopsis}
              </p>
              <button
                onClick={() => setPlayingVideo(true)}
                className="flex items-center justify-center px-8 py-3 bg-white text-black font-bold rounded hover:bg-white/80 transition-colors"
              >
                <svg className="w-6 h-6 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" />
                </svg>
                Play
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 pt-12 space-y-16">
        {/* Trailers */}
        {hasTrailers && (
          <section>
            <h2 className="text-2xl font-bold text-white mb-6">Trailers & More</h2>
            <div className="flex gap-4 overflow-x-auto pb-4 scrollbar-hide">
              {show.trailers.map((trailer, idx) => (
                <div key={idx} onClick={() => setPlayingVideo(true)} className="flex-none w-72 bg-[#141414] group cursor-pointer">
                  <div className="aspect-video bg-gray-800 flex items-center justify-center relative rounded overflow-hidden shadow-lg">
                    <ImageWithFallback src={trailer.artwork?.thumbnail} type="thumbnail" title={trailer.title} className="absolute inset-0 w-full h-full" />
                    <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 flex items-center justify-center transition-opacity z-10">
                      <svg className="w-12 h-12 text-white drop-shadow-lg" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" />
                      </svg>
                    </div>
                    <div className="absolute bottom-2 right-2 px-1.5 py-0.5 bg-black/80 text-[11px] font-bold text-white rounded z-10">
                      {Math.floor(trailer.duration / 60)}:{(trailer.duration % 60).toString().padStart(2, '0')}
                    </div>
                  </div>
                  <div className="py-3">
                    <h3 className="text-base font-bold text-gray-200 group-hover:text-white truncate">{trailer.title}</h3>
                    <p className="text-sm text-gray-500 mt-1 font-medium">{trailer.languages.join(', ')}</p>
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Seasons */}
        {hasSeasons ? (
          <div className="space-y-12">
            {show.seasons.map((season: CatalogueSeason) => (
              <section key={season.season_number}>
                <h2 className="text-2xl font-bold text-white mb-6">
                  Season {season.season_number}
                </h2>
                <div className="flex flex-col">
                  {season.episodes.map((ep: CatalogueEpisode) => (
                    <div key={ep.episode_number} onClick={() => setPlayingVideo(true)} className="flex flex-col md:flex-row gap-6 p-4 border-b border-gray-800 hover:bg-[#333] transition-colors cursor-pointer group">
                      <div className="flex items-center gap-6 md:w-1/4">
                        <span className="text-2xl font-bold text-gray-500 group-hover:text-white w-6 text-center">
                          {ep.episode_number}
                        </span>
                        <div className="w-32 md:w-40 flex-shrink-0 rounded overflow-hidden relative shadow-lg">
                          <ImageWithFallback src={ep.artwork?.thumbnail} type="thumbnail" title={ep.title} className="w-full" />
                          {ep.duration && (
                            <div className="absolute bottom-1 right-1 px-1.5 py-0.5 bg-black/80 text-[10px] font-bold text-white rounded">
                              {Math.floor(ep.duration / 60)}:{(ep.duration % 60).toString().padStart(2, '0')}
                            </div>
                          )}
                          <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 flex items-center justify-center transition-opacity">
                            <svg className="w-10 h-10 text-white drop-shadow-lg" fill="currentColor" viewBox="0 0 20 20">
                              <path d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" />
                            </svg>
                          </div>
                        </div>
                      </div>
                      <div className="flex-1 flex flex-col justify-center min-w-0">
                        <div className="flex justify-between items-center mb-2">
                          <h3 className="text-base font-bold text-white truncate">
                            {ep.title}
                          </h3>
                        </div>
                        <p className="text-sm text-gray-400 line-clamp-3 mb-2 font-medium leading-relaxed">
                          {ep.description || 'No description available.'}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </section>
            ))}
          </div>
        ) : (
          !hasTrailers && <p className="text-gray-500 text-center py-12 text-lg">No episodes available yet.</p>
        )}
      </div>
    </div>
  );
}
