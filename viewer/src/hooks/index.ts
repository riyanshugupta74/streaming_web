import { useState, useEffect } from 'react';
import { catalogApi } from '../api/client';
import type { Catalogue } from '../types';

export function useCatalogue() {
  const [data, setData] = useState<Catalogue | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    let mounted = true;
    const fetch = async () => {
      try {
        setLoading(true);
        const res = await catalogApi.get();
        if (mounted) setData(res.data);
      } catch (err: any) {
        if (mounted) setError(err);
      } finally {
        if (mounted) setLoading(false);
      }
    };
    fetch();
    return () => { mounted = false; };
  }, []);

  return { data, loading, error };
}

export function useSearch(params: { q?: string; category?: string; language?: string; section?: string }) {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    let mounted = true;
    const fetch = async () => {
      // Don't search if all params are empty
      if (!params.q && !params.category && !params.language && !params.section) {
        if (mounted) setData({ sections: [], total_results: 0 });
        return;
      }
      try {
        setLoading(true);
        const res = await catalogApi.search(params);
        if (mounted) setData(res.data);
      } catch (err: any) {
        if (mounted) setError(err);
      } finally {
        if (mounted) setLoading(false);
      }
    };
    // Debounce slightly to avoid excessive requests while typing
    const timer = setTimeout(fetch, 300);
    return () => {
      mounted = false;
      clearTimeout(timer);
    };
  }, [params.q, params.category, params.language, params.section]);

  return { data, loading, error };
}
