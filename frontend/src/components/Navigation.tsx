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
        padding: "16px 24px",
        backgroundColor: "var(--color-surface)",
        borderBottom: "1px solid var(--color-border)",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        position: "sticky",
        top: 0,
        zIndex: 100,
        boxShadow: "var(--shadow)",
      }}
    >
      {/* Logo/Title */}
      <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
        <div
          style={{
            width: "32px",
            height: "32px",
            background: "linear-gradient(135deg, var(--color-primary), var(--color-primary-light))",
            borderRadius: "8px",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: "18px",
          }}
        >
          📈
        </div>
        <h1
          style={{
            margin: 0,
            fontSize: "20px",
            fontWeight: "600",
            color: "var(--color-text)",
            background: "linear-gradient(135deg, var(--color-text), var(--color-primary-light))",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
            backgroundClip: "text",
          }}
        >
          Crypto Tracker
        </h1>
      </div>

      {/* Navigation Controls */}
      <div style={{ display: "flex", alignItems: "center", gap: "24px" }}>
        {/* View Selection */}
        <div style={{ display: "flex", gap: "4px", padding: "4px", backgroundColor: "var(--color-background)", borderRadius: "var(--border-radius)" }}>
          <button
            onClick={() => onViewChange("charts")}
            className={`btn ${currentView === "charts" ? "btn-active" : "btn-inactive"}`}
            style={{
              padding: "8px 16px",
              fontSize: "14px",
              borderRadius: "6px",
              transition: "all 0.2s ease",
              border: "none",
              cursor: "pointer",
            }}
          >
            📊 Charts
          </button>
          <button
            onClick={() => onViewChange("pairs-table")}
            className={`btn ${currentView === "pairs-table" ? "btn-active" : "btn-inactive"}`}
            style={{
              padding: "8px 16px",
              fontSize: "14px",
              borderRadius: "6px",
              transition: "all 0.2s ease",
              border: "none",
              cursor: "pointer",
            }}
          >
            📋 Pairs
          </button>
        </div>

        {/* Chart Type Selection (only visible when on charts view) */}
        {currentView === "charts" && (
          <>
            <div
              style={{
                width: "1px",
                height: "24px",
                backgroundColor: "var(--color-border)",
              }}
            />
            <div style={{ display: "flex", gap: "4px", padding: "4px", backgroundColor: "var(--color-background)", borderRadius: "var(--border-radius)" }}>
              <button
                onClick={() => onChartTypeChange("line")}
                className={`btn ${currentChartType === "line" ? "btn-active" : "btn-inactive"}`}
                style={{
                  padding: "8px 16px",
                  fontSize: "14px",
                  borderRadius: "6px",
                  transition: "all 0.2s ease",
                  border: "none",
                  cursor: "pointer",
                }}
                title="Line Chart - Compare price trends"
              >
                📈 Line
              </button>
              <button
                onClick={() => onChartTypeChange("ohlc")}
                className={`btn ${currentChartType === "ohlc" ? "btn-active" : "btn-inactive"}`}
                style={{
                  padding: "8px 16px",
                  fontSize: "14px",
                  borderRadius: "6px",
                  transition: "all 0.2s ease",
                  border: "none",
                  cursor: "pointer",
                }}
                title="OHLC Chart - Detailed price analysis"
              >
                📊 OHLC
              </button>
            </div>
          </>
        )}
      </div>
    </nav>
  );
};

export default Navigation;
