import { useState, useCallback } from 'react';
import { chartApi } from '../api/services';
import type { UseChartDataExtended, CompareParams, ChartDataResponse, LineDataResponse, DataMetadata } from '../types';

// Define proper response types instead of using 'any'
interface ApiResponseWithMetadata {
  data: unknown;
  metadata: DataMetadata;
}

interface ApiResponseLegacy {
  [key: string]: unknown;
}

type ApiResponse = ApiResponseWithMetadata | ApiResponseLegacy;

export const useChartData = (): UseChartDataExtended => {
  const [data, setData] = useState<ChartDataResponse | null>(null);
  const [lineData, setLineData] = useState<LineDataResponse | null>(null);
  const [metadata, setMetadata] = useState<DataMetadata | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [lastParams, setLastParams] = useState<CompareParams | null>(null);

  const handleResponse = (response: ApiResponse): { data: unknown; metadata: DataMetadata | null } => {
    // Check if response has new metadata format
    if (response && typeof response === 'object' && 'data' in response && 'metadata' in response) {
      // New format with metadata
      return {
        data: response.data,
        metadata: response.metadata
      };
    } else {
      // Legacy format - just data
      return {
        data: response,
        metadata: null
      };
    }
  };

  const fetchData = useCallback(async (params: CompareParams) => {
    try {
      setLoading(true);
      setError(null);
      setLastParams(params);

      console.log('[Chart] Fetching OHLC data with params:', params);

      const response = await chartApi.getCompareData(params);
      
      console.log('[Chart] Raw OHLC data response:', response);
      
      const { data: chartData, metadata: responseMetadata } = handleResponse(response);
      
      // Validate the response structure and handle real API data
      if (chartData && typeof chartData === 'object') {
        // Handle both empty arrays and valid data from real APIs
        const hasValidData = Object.values(chartData).some(data => 
          Array.isArray(data) && data.length > 0
        );
        
        if (hasValidData) {
          setData(chartData as ChartDataResponse);
          setMetadata(responseMetadata);
          console.log('[Chart] Metadata received:', responseMetadata);
        } else {
          console.warn('[Chart] No chart data available for the selected parameters');
          setError('No chart data available for the selected cryptocurrency pair and exchanges. Please try different parameters.');
          setData(null);
          setMetadata(null);
        }
      } else {
        console.warn('[Chart] Invalid OHLC data structure:', chartData);
        setError('Invalid chart data format received from server');
        setData(null);
        setMetadata(null);
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch chart data';
      console.error('Error fetching chart data:', err);
      
      // Provide more helpful error messages for common issues
      if (errorMessage.includes('timeout') || errorMessage.includes('Request timeout')) {
        setError('Request timed out. The cryptocurrency exchanges may be slow to respond. Please try again.');
      } else if (errorMessage.includes('Network request failed') || errorMessage.includes('Failed to fetch')) {
        setError('Network error. Please check your connection and try again.');
      } else if (errorMessage.includes('HTTP 5')) {
        setError('Server error. The cryptocurrency data service may be temporarily unavailable.');
      } else {
        setError(errorMessage);
      }
      
      setData(null);
      setMetadata(null);
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchLineData = useCallback(async (params: CompareParams) => {
    try {
      setLoading(true);
      setError(null);
      setLastParams(params);

      console.log('[Chart] Fetching line data with params:', params);

      // Use the line-compare endpoint which returns { time, open } format
      const response = await chartApi.getLineCompareData(params);
      
      console.log('[Chart] Raw line data response:', response);
      
      const { data: rawLineData, metadata: responseMetadata } = handleResponse(response);
      
      // Convert { time, open } data to { time, value } format for line charts
      const convertedLineData: LineDataResponse = {};
      let hasValidData = false;
      
      if (rawLineData && typeof rawLineData === 'object') {
        Object.entries(rawLineData).forEach(([exchangeName, linePoints]) => {
          // Validate that linePoints is an array before mapping
          if (Array.isArray(linePoints) && linePoints.length > 0) {
            convertedLineData[exchangeName] = linePoints.map((item: { time: number; open: number }) => ({
              time: Math.floor(item.time), // Ensure integer timestamp
              value: item.open // Backend sends 'open' field, we map it to 'value'
            }));
            hasValidData = true;
          } else {
            console.warn(`[Chart] Invalid or empty data structure for ${exchangeName}:`, linePoints);
            convertedLineData[exchangeName] = []; // Provide empty array as fallback
          }
        });
      }
      
      if (hasValidData) {
        console.log('[Chart] Converted line data:', convertedLineData);
        setLineData(convertedLineData);
        setMetadata(responseMetadata);
        console.log('[Chart] Metadata received:', responseMetadata);
      } else {
        console.warn('[Chart] No valid line data available');
        setError('No chart data available for the selected cryptocurrency pair and exchanges. Please try different parameters.');
        setLineData(null);
        setMetadata(null);
      }
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch line chart data';
      console.error('Error fetching line chart data:', err);
      
      // Provide more helpful error messages
      if (errorMessage.includes('timeout') || errorMessage.includes('Request timeout')) {
        setError('Request timed out. The cryptocurrency exchanges may be slow to respond. Please try again.');
      } else if (errorMessage.includes('Network request failed') || errorMessage.includes('Failed to fetch')) {
        setError('Network error. Please check your connection and try again.');
      } else if (errorMessage.includes('HTTP 5')) {
        setError('Server error. The cryptocurrency data service may be temporarily unavailable.');
      } else {
        setError(errorMessage);
      }
      
      setLineData(null);
      setMetadata(null);
    } finally {
      setLoading(false);
    }
  }, []);

  const refreshData = useCallback(() => {
    if (lastParams) {
      console.log('[Chart] Refreshing data with last params:', lastParams);
      // Determine which type of data to refresh based on what was last loaded
      if (lineData) {
        fetchLineData(lastParams);
      } else if (data) {
        fetchData(lastParams);
      }
    }
  }, [lastParams, lineData, data, fetchData, fetchLineData]);

  return {
    data,
    lineData,
    loading,
    error,
    metadata,
    fetchData,
    fetchLineData,
    refreshData,
  };
};