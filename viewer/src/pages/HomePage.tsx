import { Link } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { useCatalogue } from '../hooks';
import ImageWithFallback from '../components/ImageWithFallback';
import type { CatalogueShow } from '../types';

export default function HomePage() {
  const { data: catalogue, loading, error } = useCatalogue();
  const [playingVideo, setPlayingVideo] = useState(false);
  const [showHeroVideo, setShowHeroVideo] = useState(false);

  useEffect(() => {
    // Fade in the video after 3 seconds, just like Netflix
    const timer = setTimeout(() => setShowHeroVideo(true), 3000);
    return () => clearTimeout(timer);
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] space-y-4">
        <div className="w-12 h-12 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
        <p className="text-gray-400">Loading catalogue...</p>
      </div>
    );
  }

  if (error || !catalogue) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh]">
        <div className="bg-red-900/20 text-red-400 px-6 py-4 rounded-lg border border-red-900/50">
          <p className="font-medium">Failed to load content</p>
          <p className="text-sm mt-1 opacity-80">The catalogue may not be published yet.</p>
        </div>
      </div>
    );
  }

  if (!catalogue.sections || catalogue.sections.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh]">
        <p className="text-gray-400 text-lg">No content available.</p>
      </div>
    );
  }

  // Find a hero show (first show with a banner in the first section)
  let heroShow: CatalogueShow | null = null;
  for (const section of catalogue.sections) {
    for (const show of section.shows) {
      if (show.artwork?.banner) {
        heroShow = show;
        break;
      }
    }
    if (heroShow) break;
  }

  return (
    <div className="flex flex-col gap-0 pb-12">
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

      {/* Hero Section */}
      {heroShow && (
        <div className="relative w-full h-[85vh] min-h-[600px] bg-[#141414] overflow-hidden group">
          <ImageWithFallback
            src={heroShow.artwork.banner}
            type="banner"
            title={heroShow.title}
            className={`absolute inset-0 w-full h-full object-cover transition-opacity duration-1000 ${showHeroVideo ? 'opacity-0' : 'opacity-100'}`}
          />
          {showHeroVideo && (
            <video
              src="https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4"
              autoPlay
              muted
              loop
              playsInline
              className="absolute inset-0 w-full h-full object-cover"
            />
          )}
          <div className="absolute inset-0 bg-gradient-to-t from-[#141414] via-[#141414]/20 to-transparent" />
          <div className="absolute inset-0 bg-gradient-to-r from-[#141414] via-[#141414]/40 to-transparent" />
          
          <div className="absolute bottom-0 left-0 w-full p-4 sm:p-8 lg:p-12 mb-10">
            <div className="max-w-3xl">
              <h1 className="text-5xl md:text-7xl font-black text-white mb-4 drop-shadow-2xl uppercase tracking-tight">
                {heroShow.title}
              </h1>
              <div className="flex items-center space-x-4 mb-6 text-sm font-bold drop-shadow-md">
                <span className="text-green-500">98% Match</span>
                <span className="border border-gray-400 px-1 text-gray-300">HD</span>
                <span>{heroShow.category}</span>
              </div>
              <p className="text-lg md:text-xl text-white mb-8 line-clamp-3 drop-shadow-lg max-w-2xl font-medium">
                {heroShow.synopsis}
              </p>
              <div className="flex flex-row gap-4">
                <button
                  onClick={() => setPlayingVideo(true)}
                  className="flex items-center justify-center px-8 py-3 bg-white text-black font-bold rounded hover:bg-white/80 transition-colors"
                >
                  <svg className="w-6 h-6 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" />
                  </svg>
                  Play
                </button>
                <Link
                  to={`/show/${heroShow.id}`}
                  className="flex items-center justify-center px-8 py-3 bg-gray-500/40 text-white font-bold rounded hover:bg-gray-500/60 transition-colors"
                >
                  <svg className="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  More Info
                </Link>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Rows */}
      <div className="space-y-16 -mt-10 relative z-10">
        {catalogue.sections.map((section) => (
          section.shows.length > 0 && (
            <section key={section.name}>
              <h2 className="text-xl md:text-2xl font-bold text-gray-200 mb-4 px-4 sm:px-6 lg:px-12 transition-colors hover:text-white">
                {section.name}
              </h2>
              <div className="flex gap-2 overflow-x-auto pb-8 scrollbar-hide px-4 sm:px-6 lg:px-12 group/row">
                {section.shows.map((show) => (
                  <Link
                    key={show.id}
                    to={`/show/${show.id}`}
                    className="flex-none w-36 sm:w-48 md:w-56 group relative rounded overflow-hidden bg-[#141414] transition-all duration-300 hover:scale-110 hover:z-20 hover:shadow-2xl hover:shadow-black/50"
                  >
                    <ImageWithFallback
                      src={show.artwork?.poster}
                      type="poster"
                      title={show.title}
                      className="w-full h-full object-cover rounded"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/40 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex flex-col justify-end p-4">
                      <h3 className="text-sm md:text-base font-bold text-white truncate drop-shadow-md">{show.title}</h3>
                      <p className="text-xs text-gray-300 mt-1 drop-shadow-md font-medium">{show.category}</p>
                    </div>
                  </Link>
                ))}
              </div>
            </section>
          )
        ))}
      </div>
    </div>
  );
}
