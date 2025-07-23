import { useState, useEffect, useCallback } from 'react';
import { configApi } from '../api/services';
import type { PairsExchangesResponse } from '../types';

export interface UsePairsData {
  pairsData: PairsExchangesResponse | null;
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

export const usePairsData = (): UsePairsData => {
  const [pairsData, setPairsData] = useState<PairsExchangesResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchPairsData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await configApi.getPairsExchanges();
      setPairsData(data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch pairs data';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  }, []);

  const refetch = useCallback(async () => {
    await fetchPairsData();
  }, [fetchPairsData]);

  useEffect(() => {
    fetchPairsData();
  }, [fetchPairsData]);

  return {
    pairsData,
    loading,
    error,
    refetch,
  };
};
