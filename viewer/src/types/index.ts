/** TypeScript types for the Viewer application. */

export interface CatalogueEpisode {
  content_group: string;
  episode_number: number;
  title: string;
  description: string;
  duration: number;
  languages: string[];
  artwork: {
    thumbnail?: string;
  };
}

export interface CatalogueSeason {
  season_number: number;
  title: string;
  episodes: CatalogueEpisode[];
}

export interface CatalogueTrailer {
  content_group: string;
  title: string;
  duration: number;
  languages: string[];
  artwork: {
    thumbnail?: string;
  };
}

export interface CatalogueShow {
  id: string;
  title: string;
  synopsis: string;
  category: string;
  artwork: {
    poster?: string;
    banner?: string;
  };
  seasons: CatalogueSeason[];
  trailers: CatalogueTrailer[];
}

export interface CatalogueSection {
  name: string;
  shows: CatalogueShow[];
}

export interface Catalogue {
  version: string;
  published_at: string;
  sections: CatalogueSection[];
}
