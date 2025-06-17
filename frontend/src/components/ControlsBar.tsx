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
        padding: "20px",
        borderBottom: "1px solid #ccc",
        display: "flex",
        gap: "20px",
        alignItems: "center",
        flexWrap: "wrap",
      }}
    >
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
    </div>
  );
};

export default ControlsBar;
