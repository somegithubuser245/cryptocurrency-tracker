import { useState, useCallback } from 'react';
import { chartApi } from '../api/services';
import type { UseChartData, CompareParams, ChartDataResponse } from '../types';

export const useChartData = (): UseChartData => {
  const [data, setData] = useState<ChartDataResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async (params: CompareParams) => {
    try {
      setLoading(true);
      setError(null);

      const response = await chartApi.getCompareData(params);
      setData(response);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch chart data';
      setError(errorMessage);
      console.error('Error fetching chart data:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    data,
    loading,
    error,
    fetchData,
  };
};
