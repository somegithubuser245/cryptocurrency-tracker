import React from "react";
import type { SelectOption } from "../types";

interface SelectProps {
  label: string;
  id: string;
  value: string;
  options: SelectOption[];
  onChange: (value: string) => void;
  disabled?: boolean;
}

const Select: React.FC<SelectProps> = ({
  label,
  id,
  value,
  options,
  onChange,
  disabled = false,
}) => {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
      <label 
        htmlFor={id}
        style={{ 
          fontSize: "13px", 
          fontWeight: "500",
          color: "var(--color-text-secondary)",
          textTransform: "uppercase",
          letterSpacing: "0.5px"
        }}
      >
        {label}
      </label>
      <select
        id={id}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        className="select"
        style={{
          opacity: disabled ? 0.5 : 1,
          cursor: disabled ? "not-allowed" : "pointer",
        }}
      >
        <option value="" disabled>
          Select {label.toLowerCase()}
        </option>
        {options.map((option) => (
          <option key={option.id} value={option.id}>
            {option.name}
          </option>
        ))}
      </select>
    </div>
  );
};

export default Select;
