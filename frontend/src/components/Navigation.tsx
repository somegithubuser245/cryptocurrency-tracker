import React from "react";
import type { ChartType, ViewType } from "../types";

interface NavigationProps {
  currentChartType: ChartType;
  onChartTypeChange: (chartType: ChartType) => void;
  currentView: ViewType;
  onViewChange: (view: ViewType) => void;
}

const Navigation: React.FC<NavigationProps> = ({
  currentChartType,
  onChartTypeChange,
  currentView,
  onViewChange,
}) => {
  return (
    <nav
      style={{
        padding: "15px 20px",
        backgroundColor: "#000000",
        borderBottom: "2px solid #333333",
        display: "flex",
        gap: "20px",
        alignItems: "center",
      }}
    >
      <h1 style={{ margin: 0, fontSize: "24px", color: "#ffffff" }}>
        Cryptocurrency Tracker
      </h1>

      <div style={{ marginLeft: "auto", display: "flex", gap: "10px", alignItems: "center" }}>
        {/* View Selection */}
        <div style={{ display: "flex", gap: "5px", marginRight: "20px" }}>
          <button
            onClick={() => onViewChange("charts")}
            style={{
              padding: "8px 16px",
              backgroundColor: currentView === "charts" ? "#007bff" : "#333333",
              color: "#ffffff",
              border: "none",
              borderRadius: "4px",
              cursor: "pointer",
              fontWeight: currentView === "charts" ? "bold" : "normal",
              fontSize: "14px",
            }}
          >
            Charts
          </button>

          <button
            onClick={() => onViewChange("pairs-table")}
            style={{
              padding: "8px 16px",
              backgroundColor: currentView === "pairs-table" ? "#007bff" : "#333333",
              color: "#ffffff",
              border: "none",
              borderRadius: "4px",
              cursor: "pointer",
              fontWeight: currentView === "pairs-table" ? "bold" : "normal",
              fontSize: "14px",
            }}
          >
            Pairs Table
          </button>
        </div>

        {/* Chart Type Selection (only visible when on charts view) */}
        {currentView === "charts" && (
          <div style={{ display: "flex", gap: "5px" }}>
            <button
              onClick={() => onChartTypeChange("line")}
              style={{
                padding: "8px 16px",
                backgroundColor:
                  currentChartType === "line" ? "#007bff" : "#555555",
                color: "#ffffff",
                border: "none",
                borderRadius: "4px",
                cursor: "pointer",
                fontWeight: currentChartType === "line" ? "bold" : "normal",
                fontSize: "14px",
              }}
            >
              Line Chart
            </button>

            <button
              onClick={() => onChartTypeChange("ohlc")}
              style={{
                padding: "8px 16px",
                backgroundColor:
                  currentChartType === "ohlc" ? "#007bff" : "#555555",
                color: "#ffffff",
                border: "none",
                borderRadius: "4px",
                cursor: "pointer",
                fontWeight: currentChartType === "ohlc" ? "bold" : "normal",
                fontSize: "14px",
              }}
            >
              OHLC Chart
            </button>
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navigation;
