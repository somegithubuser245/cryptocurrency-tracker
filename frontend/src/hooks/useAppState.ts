import { useState, useCallback } from 'react';
import type { AppState, SelectOption } from '../types';

interface UseAppStateOptions {
  exchanges: SelectOption[];
  timeRanges: SelectOption[];
  pairs: SelectOption[];
}

export const useAppState = ({ exchanges, timeRanges, pairs }: UseAppStateOptions) => {
  const [state, setState] = useState<AppState>({
    selectedExchange1: '',
    selectedExchange2: '',
    selectedTimeRange: '',
    selectedPair: '',
    chartType: 'line', // Default to line charts
  });

  // Initialize default selections when data is available
  const initializeDefaults = useCallback(() => {
    if (
      exchanges.length >= 2 &&
      timeRanges.length > 0 &&
      pairs.length > 0 &&
      !state.selectedExchange1 // Only set if not already set
    ) {
      setState({
        selectedExchange1: exchanges[0].id,
        selectedExchange2: exchanges[1].id,
        selectedTimeRange: timeRanges[0].id,
        selectedPair: pairs[0].id,
        chartType: 'line', // Default to line charts
      });
    }
  }, [exchanges, timeRanges, pairs, state.selectedExchange1]);

  const updateState = useCallback((updates: Partial<AppState>) => {
    setState((prevState) => ({ ...prevState, ...updates }));
  }, []);

  // Check if all required selections are made
  const isComplete = Boolean(
    state.selectedExchange1 &&
    state.selectedExchange2 &&
    state.selectedTimeRange &&
    state.selectedPair
  );

  return {
    state,
    updateState,
    initializeDefaults,
    isComplete,
  };
};
