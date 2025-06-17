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
    <div>
      <label htmlFor={id}>{label}: </label>
      <select
        id={id}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        style={{ padding: "8px", marginLeft: "8px" }}
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
