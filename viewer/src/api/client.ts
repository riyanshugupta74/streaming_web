/** API client for the Viewer application. */

import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
  baseURL: API_BASE,
});

export const catalogApi = {
  get: () => api.get('/catalog'),
  search: (params: { q?: string; category?: string; language?: string; section?: string }) =>
    api.get('/catalog/search', { params }),
};
