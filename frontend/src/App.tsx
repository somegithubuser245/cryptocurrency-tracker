import { useEffect, useState } from "react";
import ChartCard from "./components/ChartCard";

function App() {
  const [exchangesData, setExchangesData] = useState<
    Array<{ id: string; name: string }>
  >([]);
  const [timeRangesData, setTimeRanges] = useState<
    Array<{ id: string; name: string }>
  >([]);
  const [pairsData, setPairsData] = useState<
    Array<{ id: string; name: string }>
  >([]);
  const [selectedExchange1, setSelectedExchange1] = useState<string>("");
  const [selectedExchange2, setSelectedExchange2] = useState<string>("");
  const [selectedTimeRange, setSelectedTimeRange] = useState<string>("");
  const [selectedPair, setSelectedPair] = useState<string>("");
  const [chartData, setChartData] = useState<any>(null);

  useEffect(() => {
    let ignore = false;

    async function fetchConfigData() {
      try {
        // Fetch exchanges
        let response = await fetch(
          "http://127.0.0.1:8000/static/config/exchanges"
        );
        let data = await response.json();
        let processedExchangesData: Array<{ id: string; name: string }> = [];
        Object.entries(data).forEach((entry) => {
          processedExchangesData.push({
            id: entry[0],
            name: entry[1] as string,
          });
        });

        // Fetch time ranges
        response = await fetch(
          "http://127.0.0.1:8000/static/config/timeranges"
        );
        data = await response.json();
        let processedRangesData: Array<{ id: string; name: string }> = [];
        Object.entries(data).forEach((entry) => {
          processedRangesData.push({ id: entry[0], name: entry[1] as string });
        });

        // Fetch pairs
        response = await fetch("http://127.0.0.1:8000/static/config/pairs");
        data = await response.json();
        let processedPairsData: Array<{ id: string; name: string }> = [];
        Object.entries(data).forEach((entry) => {
          processedPairsData.push({ id: entry[0], name: entry[1] as string });
        });

        if (!ignore) {
          setExchangesData(processedExchangesData);
          setTimeRanges(processedRangesData);
          setPairsData(processedPairsData);

          // Set default selections
          if (processedExchangesData.length >= 2) {
            setSelectedExchange1(processedExchangesData[0].id);
            setSelectedExchange2(processedExchangesData[1].id);
          }
          if (processedRangesData.length > 0) {
            setSelectedTimeRange(processedRangesData[0].id);
          }
          if (processedPairsData.length > 0) {
            setSelectedPair(processedPairsData[0].id);
          }
        }
      } catch (error) {
        console.error("Error fetching config data:", error);
      }
    }

    fetchConfigData();

    return () => {
      ignore = true;
    };
  }, []);

  // Fetch chart data when selections change
  useEffect(() => {
    if (
      selectedExchange1 &&
      selectedExchange2 &&
      selectedTimeRange &&
      selectedPair
    ) {
      fetchChartData();
    }
  }, [selectedExchange1, selectedExchange2, selectedTimeRange, selectedPair]);

  async function fetchChartData() {
    try {
      const response = await fetch(
        `http://127.0.0.1:8000/compare?exchange1=${selectedExchange1}&exchange2=${selectedExchange2}&interval=${selectedTimeRange}&crypto_id=${selectedPair}`
      );
      const data = await response.json();
      setChartData(data);
    } catch (error) {
      console.error("Error fetching chart data:", error);
    }
  }

  return (
    <div className="app">
      {/* Top bar with dropdowns */}
      <div
        className="controls-bar"
        style={{
          padding: "20px",
          borderBottom: "1px solid #ccc",
          display: "flex",
          gap: "20px",
          alignItems: "center",
          flexWrap: "wrap",
        }}
      >
        <div>
          <label htmlFor="exchange1">Exchange 1: </label>
          <select
            id="exchange1"
            value={selectedExchange1}
            onChange={(e) => setSelectedExchange1(e.target.value)}
            style={{ padding: "8px", marginLeft: "8px" }}
          >
            {exchangesData.map((exchange) => (
              <option key={exchange.id} value={exchange.id}>
                {exchange.name}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label htmlFor="exchange2">Exchange 2: </label>
          <select
            id="exchange2"
            value={selectedExchange2}
            onChange={(e) => setSelectedExchange2(e.target.value)}
            style={{ padding: "8px", marginLeft: "8px" }}
          >
            {exchangesData.map((exchange) => (
              <option key={exchange.id} value={exchange.id}>
                {exchange.name}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label htmlFor="pair">Crypto Pair: </label>
          <select
            id="pair"
            value={selectedPair}
            onChange={(e) => setSelectedPair(e.target.value)}
            style={{ padding: "8px", marginLeft: "8px" }}
          >
            {pairsData.map((pair) => (
              <option key={pair.id} value={pair.id}>
                {pair.name}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label htmlFor="timerange">Time Range: </label>
          <select
            id="timerange"
            value={selectedTimeRange}
            onChange={(e) => setSelectedTimeRange(e.target.value)}
            style={{ padding: "8px", marginLeft: "8px" }}
          >
            {timeRangesData.map((range) => (
              <option key={range.id} value={range.id}>
                {range.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Charts section */}
      {chartData && (
        <div
          className="charts-container"
          style={{
            display: "flex",
            flexDirection: "column",
            gap: "20px",
            padding: "20px",
          }}
        >
          <ChartCard
            title={`${
              exchangesData.find((e) => e.id === selectedExchange1)?.name ||
              selectedExchange1
            } - ${
              pairsData.find((p) => p.id === selectedPair)?.name || selectedPair
            }`}
            data={chartData[selectedExchange1]}
            api_provider={selectedExchange1}
          />
          <ChartCard
            title={`${
              exchangesData.find((e) => e.id === selectedExchange2)?.name ||
              selectedExchange2
            } - ${
              pairsData.find((p) => p.id === selectedPair)?.name || selectedPair
            }`}
            data={chartData[selectedExchange2]}
            api_provider={selectedExchange2}
          />
        </div>
      )}
    </div>
  );
}

export default App;
