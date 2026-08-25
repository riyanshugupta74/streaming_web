/** Custom hooks for the CMS application. */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { showsApi, seasonsApi, episodesApi, artworkApi, publishApi } from '../api/client';
import type { ShowListResponse, Show, ValidationReport, PublishRun, PublishResponse } from '../types';

// ─── Auth Hook ─────────────────────────────────────────────────────────────

export function useAuth() {
  const getUser = () => {
    const userStr = localStorage.getItem('user');
    if (!userStr) return null;
    try {
      return JSON.parse(userStr);
    } catch {
      return null;
    }
  };

  const getToken = () => localStorage.getItem('token');
  const isAuthenticated = () => !!getToken();
  const isAdmin = () => getUser()?.role === 'admin';
  const user = getUser();

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/login';
  };

  return { user, getToken, isAuthenticated, isAdmin, logout };
}

// ─── Shows Hooks ───────────────────────────────────────────────────────────

export function useShows(params: Record<string, string | number | undefined>) {
  return useQuery<ShowListResponse>({
    queryKey: ['shows', params],
    queryFn: async () => {
      const res = await showsApi.list(params);
      return res.data;
    },
  });
}

export function useShow(id: string) {
  return useQuery<Show>({
    queryKey: ['show', id],
    queryFn: async () => {
      const res = await showsApi.get(id);
      return res.data;
    },
    enabled: !!id,
  });
}

export function useCreateShow() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Record<string, unknown>) => showsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['shows'] });
    },
  });
}

export function useUpdateShow() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Record<string, unknown> }) =>
      showsApi.update(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['shows'] });
      queryClient.invalidateQueries({ queryKey: ['show', variables.id] });
    },
  });
}

export function useDeleteShow() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => showsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['shows'] });
    },
  });
}

// ─── Season Hooks ──────────────────────────────────────────────────────────

export function useCreateSeason() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ showId, data }: { showId: string; data: Record<string, unknown> }) =>
      seasonsApi.create(showId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['show'] });
    },
  });
}

export function useDeleteSeason() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => seasonsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['show'] });
    },
  });
}

// ─── Episode Hooks ─────────────────────────────────────────────────────────

export function useCreateEpisode() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ seasonId, data }: { seasonId: string; data: Record<string, unknown> }) =>
      episodesApi.create(seasonId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['show'] });
    },
  });
}

export function useUpdateEpisode() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Record<string, unknown> }) =>
      episodesApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['show'] });
    },
  });
}

export function useDeleteEpisode() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => episodesApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['show'] });
    },
  });
}

// ─── Artwork Hooks ─────────────────────────────────────────────────────────

export function useUploadArtwork() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (formData: FormData) => artworkApi.upload(formData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['show'] });
    },
  });
}

export function useDeleteArtwork() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => artworkApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['show'] });
    },
  });
}

// ─── Validation & Publishing Hooks ─────────────────────────────────────────

export function useValidationReport() {
  return useQuery<ValidationReport>({
    queryKey: ['validation-report'],
    queryFn: async () => {
      const res = await publishApi.getValidationReport();
      return res.data;
    },
  });
}

export function usePublish() {
  const queryClient = useQueryClient();
  return useMutation<{ data: PublishResponse }>({
    mutationFn: () => publishApi.publish(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['validation-report'] });
      queryClient.invalidateQueries({ queryKey: ['publish-runs'] });
    },
  });
}

export function usePublishRuns() {
  return useQuery<PublishRun[]>({
    queryKey: ['publish-runs'],
    queryFn: async () => {
      const res = await publishApi.getPublishRuns();
      return res.data;
    },
  });
}
