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
        setLoading(true);
        setError(null);

        const [exchangesResponse, timeRangesResponse, pairsResponse] = await Promise.all([
          configApi.getExchanges(),
          configApi.getTimeRanges(),
          configApi.getPairs(),
        ]);

        if (!ignore) {
          setExchanges(transformConfigToOptions(exchangesResponse));
          setTimeRanges(transformConfigToOptions(timeRangesResponse));
          setPairs(transformConfigToOptions(pairsResponse));
        }
      } catch (err) {
        if (!ignore) {
          const errorMessage = err instanceof Error ? err.message : 'Failed to fetch configuration data';
          setError(errorMessage);
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
