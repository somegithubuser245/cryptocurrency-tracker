import { useState, useEffect } from 'react';
import { configApi } from '../api/services';
import type { UseConfigData, SelectOption } from '../types';

const transformConfigToOptions = (config: Record<string, string>): SelectOption[] => {
  return Object.entries(config).map(([id, name]) => ({ id, name }));
};

export const useConfigData = (): UseConfigData => {
  const [exchanges, setExchanges] = useState<SelectOption[]>([]);
  const [timeRanges, setTimeRanges] = useState<SelectOption[]>([]);
  const [pairs, setPairs] = useState<SelectOption[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let ignore = false;

    const fetchConfigData = async () => {
      try {
        console.log('[Config] Loading configuration data...');
        setLoading(true);
        setError(null);
        const startTime = performance.now();

        const [exchangesResponse, timeRangesResponse, pairsResponse] = await Promise.all([
          configApi.getExchanges(),
          configApi.getTimeRanges(),
          configApi.getPairs(),
        ]);

        if (!ignore) {
          const loadTime = performance.now() - startTime;
          console.log(`[Config] Config data loaded in ${loadTime.toFixed(2)}ms`);
          
          setExchanges(transformConfigToOptions(exchangesResponse));
          setTimeRanges(transformConfigToOptions(timeRangesResponse));
          setPairs(transformConfigToOptions(pairsResponse));
        }
      } catch (err) {
        if (!ignore) {
          const errorMessage = err instanceof Error ? err.message : 'Failed to fetch configuration data';
          
          // Provide more helpful error messages
          if (errorMessage.includes('timeout') || errorMessage.includes('Request timeout')) {
            setError('Configuration loading timed out. The server may be busy loading cryptocurrency data. Please try again.');
          } else if (errorMessage.includes('Network request failed') || errorMessage.includes('Failed to fetch')) {
            setError('Network error. Please check your connection and try again.');
          } else if (errorMessage.includes('HTTP 5')) {
            setError('Server error. The cryptocurrency data service may be temporarily unavailable.');
          } else {
            setError(errorMessage);
          }
          
          console.error('Error fetching config data:', err);
        }
      } finally {
        if (!ignore) {
          setLoading(false);
        }
      }
    };

    fetchConfigData();

    return () => {
      ignore = true;
    };
  }, []);

  return {
    exchanges,
    timeRanges,
    pairs,
    loading,
    error,
  };
};
