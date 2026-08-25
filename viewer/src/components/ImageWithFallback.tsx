import { useState } from 'react';

interface ImageProps extends React.ImgHTMLAttributes<HTMLImageElement> {
  fallbackSrc?: string;
  type: 'poster' | 'banner' | 'thumbnail';
  title?: string;
}

export default function ImageWithFallback({ src, fallbackSrc, type, title, className = '', ...props }: ImageProps) {
  const [loaded, setLoaded] = useState(false);
  const [error, setError] = useState(false);

  const apiBase = import.meta.env.VITE_API_URL || '/api';
  const finalSrc = src ? (src.startsWith('http') ? src : `${apiBase}${src}`) : fallbackSrc;

  // Aspect ratios based on type
  const aspectRatioClass = {
    poster: 'aspect-[2/3]',
    banner: 'aspect-video',
    thumbnail: 'aspect-video',
  }[type];

  if (!finalSrc || error) {
    const dimensions = {
      poster: '400x600',
      banner: '1200x600',
      thumbnail: '600x400'
    }[type];
    
    const text = title ? encodeURIComponent(title) : 'Image+Unavailable';
    const placeholdSrc = `https://placehold.co/${dimensions}/141414/ffffff?text=${text}`;

    return (
      <div className={`relative bg-[#141414] overflow-hidden ${aspectRatioClass} ${className}`}>
        {!loaded && (
          <div className="absolute inset-0 bg-[#222] animate-pulse" />
        )}
        <img
          src={placeholdSrc}
          alt={title || 'Fallback'}
          onLoad={() => setLoaded(true)}
          className={`w-full h-full object-cover transition-opacity duration-300 ${loaded ? 'opacity-100' : 'opacity-0'}`}
          {...props}
        />
      </div>
    );
  }

  return (
    <div className={`relative bg-gray-900 overflow-hidden ${aspectRatioClass} ${className}`}>
      {/* Skeleton loader */}
      {!loaded && (
        <div className="absolute inset-0 bg-gray-800 animate-pulse" />
      )}
      <img
        src={finalSrc}
        onLoad={() => setLoaded(true)}
        onError={() => setError(true)}
        className={`w-full h-full object-cover transition-opacity duration-300 ${loaded ? 'opacity-100' : 'opacity-0'}`}
        {...props}
      />
    </div>
  );
}
