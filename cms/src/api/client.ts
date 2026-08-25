/** API client for the CMS application. */

import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
  baseURL: API_BASE,
});

// Add auth token to all requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 responses globally
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;

// ─── Auth ──────────────────────────────────────────────────────────────────

export const authApi = {
  login: (email: string, password: string) =>
    api.post('/auth/login', { email, password }),
  getMe: () => api.get('/auth/me'),
};

// ─── Shows ─────────────────────────────────────────────────────────────────

export const showsApi = {
  list: (params: Record<string, string | number | undefined>) =>
    api.get('/admin/shows', { params }),
  get: (id: string) => api.get(`/admin/shows/${id}`),
  create: (data: Record<string, unknown>) => api.post('/admin/shows', data),
  update: (id: string, data: Record<string, unknown>) => api.put(`/admin/shows/${id}`, data),
  delete: (id: string) => api.delete(`/admin/shows/${id}`),
};

// ─── Seasons ───────────────────────────────────────────────────────────────

export const seasonsApi = {
  create: (showId: string, data: Record<string, unknown>) =>
    api.post(`/admin/shows/${showId}/seasons`, data),
  update: (id: string, data: Record<string, unknown>) =>
    api.put(`/admin/seasons/${id}`, data),
  delete: (id: string) => api.delete(`/admin/seasons/${id}`),
};

// ─── Episodes ──────────────────────────────────────────────────────────────

export const episodesApi = {
  create: (seasonId: string, data: Record<string, unknown>) =>
    api.post(`/admin/seasons/${seasonId}/episodes`, data),
  update: (id: string, data: Record<string, unknown>) =>
    api.put(`/admin/episodes/${id}`, data),
  delete: (id: string) => api.delete(`/admin/episodes/${id}`),
};

// ─── Artwork ───────────────────────────────────────────────────────────────

export const artworkApi = {
  upload: (formData: FormData) =>
    api.post('/admin/artwork', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  delete: (id: string) => api.delete(`/admin/artwork/${id}`),
};

// ─── Validation & Publishing ───────────────────────────────────────────────

export const publishApi = {
  getValidationReport: () => api.get('/admin/validation-report'),
  publish: () => api.post('/admin/catalog/publish'),
  getPublishRuns: () => api.get('/admin/catalog/publish-runs'),
};
