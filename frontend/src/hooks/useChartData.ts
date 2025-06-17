import { useState, useCallback } from 'react';
import { chartApi } from '../api/services';
import type { UseChartData, CompareParams, ChartDataResponse, LineDataResponse } from '../types';

export const useChartData = (): UseChartData => {
  const [data, setData] = useState<ChartDataResponse | null>(null);
  const [lineData, setLineData] = useState<LineDataResponse | null>(null);
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
  }, []);  const fetchLineData = useCallback(async (params: CompareParams) => {
    try {
      setLoading(true);
      setError(null);

      // Use the line-compare endpoint which returns { time, open } format
      const response = await chartApi.getLineCompareData(params);
      
      // Convert { time, open } data to { time, value } format for line charts
      const convertedLineData: LineDataResponse = {};      Object.entries(response).forEach(([exchangeName, linePoints]) => {
        convertedLineData[exchangeName] = linePoints.map((item) => ({
          time: Math.floor(item.time), // Ensure integer timestamp
          value: item.open // Backend sends 'open' field, we map it to 'value'
        }));
      });
      
      setLineData(convertedLineData);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch line chart data';
      setError(errorMessage);
      console.error('Error fetching line chart data:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    data,
    lineData,
    loading,
    error,
    fetchData,
    fetchLineData,
  };
};
