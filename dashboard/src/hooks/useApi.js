import { useState, useCallback } from 'react';

/**
 * Generic hook for API calls with loading/error state management.
 * @param {Function} apiFunc - The API function to call
 * @returns {{ data, loading, error, execute, reset }}
 */
export function useApi(apiFunc) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const execute = useCallback(
    async (...args) => {
      setLoading(true);
      setError(null);
      try {
        const result = await apiFunc(...args);
        setData(result);
        return result;
      } catch (err) {
        const message =
          err.response?.data?.detail ||
          err.response?.data?.message ||
          err.message ||
          'An unexpected error occurred';
        setError(message);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [apiFunc]
  );

  const reset = useCallback(() => {
    setData(null);
    setLoading(false);
    setError(null);
  }, []);

  return { data, loading, error, execute, reset };
}
