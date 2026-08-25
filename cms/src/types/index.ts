/** TypeScript types for the CMS application. */

export interface User {
  id: string;
  email: string;
  role: 'editor' | 'admin';
  created_at: string;
}

export interface AuthToken {
  access_token: string;
  token_type: string;
  role: string;
  email: string;
}

export interface Artwork {
  id: string;
  type: 'poster' | 'banner' | 'thumbnail';
  storage_key: string;
  width: number;
  height: number;
  size_bytes: number;
  created_at: string;
}

export interface Episode {
  id: string;
  season_id: string;
  episode_number: number;
  title: string;
  description: string;
  duration: number | null;
  content_group: string;
  language: string;
  status: 'draft' | 'published';
  created_at: string;
  updated_at: string;
  artwork: Artwork[];
}

export interface Season {
  id: string;
  show_id: string;
  season_number: number;
  title: string;
  episodes: Episode[];
}

export interface Show {
  id: string;
  title: string;
  synopsis: string;
  category: string;
  section: string;
  status: 'draft' | 'published';
  created_at: string;
  updated_at: string;
  seasons: Season[];
  artwork: Artwork[];
}

export interface ShowListItem {
  id: string;
  title: string;
  category: string;
  section: string;
  status: 'draft' | 'published';
  updated_at: string;
  season_count: number;
  episode_count: number;
}

export interface ShowListResponse {
  items: ShowListItem[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface ValidationError {
  entity: string;
  entity_id: string | null;
  entity_name: string;
  field: string;
  problem: string;
  fix: string;
}

export interface ValidationReport {
  blocking: boolean;
  total_errors: number;
  shows: ValidationError[];
  episodes: ValidationError[];
  artwork: ValidationError[];
  metadata: ValidationError[];
}

export interface PublishRun {
  id: string;
  started_at: string;
  completed_at: string | null;
  triggered_by: string;
  status: 'running' | 'success' | 'failed' | 'blocked';
  shows_count: number;
  episodes_count: number;
  catalogue_key: string | null;
  error: string | null;
}

export interface PublishResponse {
  success: boolean;
  message: string;
  publish_run: PublishRun | null;
  validation_report: ValidationReport | null;
}
