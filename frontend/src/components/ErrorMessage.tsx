import React from "react";

interface ErrorMessageProps {
  error: string;
  onRetry?: () => void;
}

const ErrorMessage: React.FC<ErrorMessageProps> = ({ error, onRetry }) => {
  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: "20px",
        gap: "15px",
        backgroundColor: "#fee",
        border: "1px solid #fcc",
        borderRadius: "8px",
        margin: "20px",
      }}
    >
      <div
        style={{
          color: "#c33",
          fontSize: "18px",
          fontWeight: "bold",
        }}
      >
        ⚠️ Error
      </div>
      <p style={{ color: "#666", textAlign: "center", margin: 0 }}>{error}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          style={{
            padding: "8px 16px",
            backgroundColor: "#3498db",
            color: "white",
            border: "none",
            borderRadius: "4px",
            cursor: "pointer",
          }}
        >
          Retry
        </button>
      )}
    </div>
  );
};

export default ErrorMessage;
