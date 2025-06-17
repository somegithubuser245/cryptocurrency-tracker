import React from "react";
import type { ChartType } from "../types";

interface NavigationProps {
  currentChartType: ChartType;
  onChartTypeChange: (chartType: ChartType) => void;
}

const Navigation: React.FC<NavigationProps> = ({
  currentChartType,
  onChartTypeChange,
}) => {
  return (
    <nav
      style={{
        padding: "15px 20px",
        backgroundColor: "#f8f9fa",
        borderBottom: "2px solid #dee2e6",
        display: "flex",
        gap: "20px",
        alignItems: "center",
      }}
    >
      <h1 style={{ margin: 0, fontSize: "24px", color: "#333" }}>
        Cryptocurrency Tracker
      </h1>

      <div style={{ marginLeft: "auto", display: "flex", gap: "10px" }}>
        <button
          onClick={() => onChartTypeChange("line")}
          style={{
            padding: "8px 16px",
            backgroundColor:
              currentChartType === "line" ? "#007bff" : "#6c757d",
            color: "white",
            border: "none",
            borderRadius: "4px",
            cursor: "pointer",
            fontWeight: currentChartType === "line" ? "bold" : "normal",
          }}
        >
          Line Chart
        </button>

        <button
          onClick={() => onChartTypeChange("ohlc")}
          style={{
            padding: "8px 16px",
            backgroundColor:
              currentChartType === "ohlc" ? "#007bff" : "#6c757d",
            color: "white",
            border: "none",
            borderRadius: "4px",
            cursor: "pointer",
            fontWeight: currentChartType === "ohlc" ? "bold" : "normal",
          }}
        >
          OHLC Chart
        </button>
      </div>
    </nav>
  );
};

export default Navigation;
