import React from "react";
import ChartCard from "./ChartCard";
import type { ChartDataResponse, SelectOption } from "../types";

interface ChartsContainerProps {
  chartData: ChartDataResponse;
  exchanges: SelectOption[];
  pairs: SelectOption[];
  selectedExchange1: string;
  selectedExchange2: string;
  selectedPair: string;
}

const ChartsContainer: React.FC<ChartsContainerProps> = ({
  chartData,
  exchanges,
  pairs,
  selectedExchange1,
  selectedExchange2,
  selectedPair,
}) => {
  const getExchangeName = (exchangeId: string): string => {
    return exchanges.find((e) => e.id === exchangeId)?.name || exchangeId;
  };

  const getPairName = (pairId: string): string => {
    return pairs.find((p) => p.id === pairId)?.name || pairId;
  };

  return (
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
        title={`${getExchangeName(selectedExchange1)} - ${getPairName(
          selectedPair
        )}`}
        data={chartData[selectedExchange1]}
        api_provider={selectedExchange1}
      />
      <ChartCard
        title={`${getExchangeName(selectedExchange2)} - ${getPairName(
          selectedPair
        )}`}
        data={chartData[selectedExchange2]}
        api_provider={selectedExchange2}
      />
    </div>
  );
};

export default ChartsContainer;
