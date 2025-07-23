import React from "react";
import Select from "./Select";
import type { SelectOption, AppState } from "../types";

interface ControlsBarProps {
  exchanges: SelectOption[];
  timeRanges: SelectOption[];
  pairs: SelectOption[];
  state: AppState;
  onStateChange: (updates: Partial<AppState>) => void;
  disabled?: boolean;
}

const ControlsBar: React.FC<ControlsBarProps> = ({
  exchanges,
  timeRanges,
  pairs,
  state,
  onStateChange,
  disabled = false,
}) => {
  return (
    <div
      className="controls-bar"
      style={{
        padding: "24px",
        backgroundColor: "var(--color-surface)",
        borderBottom: "1px solid var(--color-border)",
        display: "flex",
        gap: "24px",
        alignItems: "center",
        flexWrap: "wrap",
        margin: 0,
      }}
    >
      <div style={{ 
        display: "flex", 
        alignItems: "center", 
        gap: "8px",
        color: "var(--color-text-secondary)",
        fontSize: "14px",
        fontWeight: "500"
      }}>
        ⚙️ Configuration:
      </div>
      
      <Select
        label="Exchange 1"
        id="exchange1"
        value={state.selectedExchange1}
        options={exchanges}
        onChange={(value) => onStateChange({ selectedExchange1: value })}
        disabled={disabled}
      />

      <Select
        label="Exchange 2"
        id="exchange2"
        value={state.selectedExchange2}
        options={exchanges}
        onChange={(value) => onStateChange({ selectedExchange2: value })}
        disabled={disabled}
      />

      <Select
        label="Crypto Pair"
        id="pair"
        value={state.selectedPair}
        options={pairs}
        onChange={(value) => onStateChange({ selectedPair: value })}
        disabled={disabled}
      />

      <Select
        label="Time Range"
        id="timerange"
        value={state.selectedTimeRange}
        options={timeRanges}
        onChange={(value) => onStateChange({ selectedTimeRange: value })}
        disabled={disabled}
      />
      
      {disabled && (
        <div style={{ 
          display: "flex", 
          alignItems: "center", 
          gap: "8px",
          color: "var(--color-text-secondary)",
          fontSize: "12px",
          fontStyle: "italic"
        }}>
          Loading...
        </div>
      )}
    </div>
  );
};

export default ControlsBar;
