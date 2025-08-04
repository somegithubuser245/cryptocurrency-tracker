import { useState } from 'react';
import { spreadApi } from '../api/services';
import type { MaxSpreadResponse, AllSpreadsResponse, SpreadRequest } from '../types';

export interface UseSpreadData {
  maxSpreadData: MaxSpreadResponse | null;
  allSpreadsData: AllSpreadsResponse | null;
  loading: boolean;
  error: string | null;
  fetchSpreads: (params: SpreadRequest) => Promise<void>;
}

export const useSpreadData = (): UseSpreadData => {
  const [maxSpreadData, setMaxSpreadData] = useState<MaxSpreadResponse | null>(null);
  const [allSpreadsData, setAllSpreadsData] = useState<AllSpreadsResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchSpreads = async (params: SpreadRequest) => {
    setLoading(true);
    setError(null);
    
    try {
      // Fetch both max spread and all spreads in parallel
      const [maxSpread, allSpreads] = await Promise.all([
        spreadApi.getMaxSpread(params),
        spreadApi.getAllSpreads(params)
      ]);
      
      setMaxSpreadData(maxSpread);
      setAllSpreadsData(allSpreads);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch spread data');
      setMaxSpreadData(null);
      setAllSpreadsData(null);
    } finally {
      setLoading(false);
    }
  };

  return {
    maxSpreadData,
    allSpreadsData,
    loading,
    error,
    fetchSpreads,
  };
};
