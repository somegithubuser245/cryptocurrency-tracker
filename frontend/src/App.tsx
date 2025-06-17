import { useEffect } from "react";
import "./App.css";
import { useConfigData } from "./hooks/useConfigData";
import { useChartData } from "./hooks/useChartData";
import { useAppState } from "./hooks/useAppState";
import ControlsBar from "./components/ControlsBar";
import ChartsContainer from "./components/ChartsContainer";
import LoadingSpinner from "./components/LoadingSpinner";
import ErrorMessage from "./components/ErrorMessage";

function App() {
  const {
    exchanges,
    timeRanges,
    pairs,
    loading: configLoading,
    error: configError,
  } = useConfigData();

  const {
    data: chartData,
    loading: chartLoading,
    error: chartError,
    fetchData: fetchChartData,
  } = useChartData();

  const { state, updateState, initializeDefaults, isComplete } = useAppState({
    exchanges,
    timeRanges,
    pairs,
  });

  // Initialize default selections when config data is loaded
  useEffect(() => {
    if (!configLoading && !configError) {
      initializeDefaults();
    }
  }, [configLoading, configError, initializeDefaults]);

  // Fetch chart data when all selections are complete
  useEffect(() => {
    if (isComplete) {
      fetchChartData({
        exchange1: state.selectedExchange1,
        exchange2: state.selectedExchange2,
        interval: state.selectedTimeRange,
        crypto_id: state.selectedPair,
      });
    }
  }, [
    state.selectedExchange1,
    state.selectedExchange2,
    state.selectedTimeRange,
    state.selectedPair,
    isComplete,
    fetchChartData,
  ]);

  const handleRetryConfig = () => {
    window.location.reload(); // Simple retry for config data
  };

  const handleRetryChart = () => {
    if (isComplete) {
      fetchChartData({
        exchange1: state.selectedExchange1,
        exchange2: state.selectedExchange2,
        interval: state.selectedTimeRange,
        crypto_id: state.selectedPair,
      });
    }
  };

  // Show loading spinner while config is loading
  if (configLoading) {
    return <LoadingSpinner message="Loading configuration..." />;
  }

  // Show error if config failed to load
  if (configError) {
    return <ErrorMessage error={configError} onRetry={handleRetryConfig} />;
  }

  return (
    <div className="app">
      <ControlsBar
        exchanges={exchanges}
        timeRanges={timeRanges}
        pairs={pairs}
        state={state}
        onStateChange={updateState}
        disabled={chartLoading}
      />

      {chartLoading && <LoadingSpinner message="Loading chart data..." />}

      {chartError && (
        <ErrorMessage error={chartError} onRetry={handleRetryChart} />
      )}

      {chartData && !chartLoading && !chartError && (
        <ChartsContainer
          chartData={chartData}
          exchanges={exchanges}
          pairs={pairs}
          selectedExchange1={state.selectedExchange1}
          selectedExchange2={state.selectedExchange2}
          selectedPair={state.selectedPair}
        />
      )}
    </div>
  );
}

export default App;
