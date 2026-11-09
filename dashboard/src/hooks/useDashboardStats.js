import { useEffect } from 'react';
import { useApi } from './useApi';
import { getDashboardStats } from '../api/client';

/**
 * Hook that fetches dashboard statistics on mount.
 * Returns data, loading, error, and a refetch function.
 */
export function useDashboardStats() {
  const { data, loading, error, execute } = useApi(getDashboardStats);

  useEffect(() => {
    execute().catch(() => {
      // Error is already captured in the hook state
    });
  }, [execute]);

  return {
    stats: data,
    loading,
    error,
    refetch: execute,
  };
}
