import { useEffect } from "react";
import "./App.css";
import { useConfigData } from "./hooks/useConfigData";
import { useChartData } from "./hooks/useChartData";
import { usePairsData } from "./hooks/usePairsData";
import { useAppState } from "./hooks/useAppState";
import Navigation from "./components/Navigation";
import ControlsBar from "./components/ControlsBar";
import ChartsContainer from "./components/ChartsContainer";
import CombinedLineChart from "./components/CombinedLineChart";
import PairsTable from "./components/PairsTable";
import LoadingSpinner from "./components/LoadingSpinner";
import ErrorMessage from "./components/ErrorMessage";
import DataSourceStatus from "./components/DataSourceStatus";

function App() {
  const {
    exchanges,
    timeRanges,
    pairs,
    loading: configLoading,
    error: configError,
  } = useConfigData();

  const {
    pairsData,
    loading: pairsLoading,
    error: pairsError,
    refetch: refetchPairs,
  } = usePairsData();

  const {
    data: chartData,
    lineData,
    loading: chartLoading,
    error: chartError,
    metadata: chartMetadata,
    fetchData: fetchChartData,
    fetchLineData: fetchLineChartData,
    refreshData: refreshChartData,
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
      const params = {
        exchange1: state.selectedExchange1,
        exchange2: state.selectedExchange2,
        interval: state.selectedTimeRange,
        crypto_id: state.selectedPair,
      };

      if (state.chartType === "line") {
        fetchLineChartData(params);
      } else {
        fetchChartData(params);
      }
    }
  }, [
    state.selectedExchange1,
    state.selectedExchange2,
    state.selectedTimeRange,
    state.selectedPair,
    state.chartType,
    isComplete,
    fetchChartData,
    fetchLineChartData,
  ]);

  const handleRetryConfig = () => {
    window.location.reload(); // Simple retry for config data
  };
  
  const handleRetryChart = () => {
    if (isComplete) {
      const params = {
        exchange1: state.selectedExchange1,
        exchange2: state.selectedExchange2,
        interval: state.selectedTimeRange,
        crypto_id: state.selectedPair,
      };

      if (state.chartType === "line") {
        fetchLineChartData(params);
      } else {
        fetchChartData(params);
      }
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
      <Navigation
        currentChartType={state.chartType}
        onChartTypeChange={(chartType) => updateState({ chartType })}
        currentView={state.currentView}
        onViewChange={(currentView) => updateState({ currentView })}
      />

      {/* Show Pairs Table View */}
      {state.currentView === "pairs-table" && (
        <PairsTable
          pairsData={pairsData}
          loading={pairsLoading}
          error={pairsError}
          onRetry={refetchPairs}
        />
      )}

      {/* Show Charts View */}
      {state.currentView === "charts" && (
        <>
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

          {/* Show line chart */}
          {state.chartType === "line" &&
            lineData &&
            !chartLoading &&
            !chartError && (
              <div className="line-chart-container">
                <CombinedLineChart
                  data1={lineData[state.selectedExchange1] || []}
                  data2={lineData[state.selectedExchange2] || []}
                  exchange1Name={
                    exchanges.find((e) => e.id === state.selectedExchange1)?.name ||
                    state.selectedExchange1
                  }
                  exchange2Name={
                    exchanges.find((e) => e.id === state.selectedExchange2)?.name ||
                    state.selectedExchange2
                  }
                  pairName={
                    pairs.find((p) => p.id === state.selectedPair)?.name ||
                    state.selectedPair
                  }
                />
              </div>
            )}

          {/* Show OHLC charts */}
          {state.chartType === "ohlc" &&
            chartData &&
            !chartLoading &&
            !chartError && (
              <div className="charts-container">
                <ChartsContainer
                  chartData={chartData}
                  exchanges={exchanges}
                  pairs={pairs}
                  selectedExchange1={state.selectedExchange1}
                  selectedExchange2={state.selectedExchange2}
                  selectedPair={state.selectedPair}
                />
              </div>
            )}
        </>
      )}

      {/* Data Source Status - shows when chart data is loaded */}
      {(chartData || lineData) && !chartLoading && (
        <DataSourceStatus
          metadata={chartMetadata}
          onRefreshRequest={refreshChartData}
          autoRefreshInterval={300} // 5 minutes
        />
      )}
    </div>
  );
}

export default App;
