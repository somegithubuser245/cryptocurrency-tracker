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
        padding: "24px",
        gap: "16px",
        backgroundColor: "var(--color-surface)",
        border: "1px solid var(--color-error)",
        borderRadius: "var(--border-radius-lg)",
        margin: "20px",
        boxShadow: "var(--shadow)",
      }}
    >
      <div
        style={{
          color: "var(--color-error)",
          fontSize: "48px",
          marginBottom: "8px",
        }}
      >
        ⚠️
      </div>
      <div
        style={{
          color: "var(--color-error)",
          fontSize: "18px",
          fontWeight: "600",
          marginBottom: "4px",
        }}
      >
        Something went wrong
      </div>
      <p 
        style={{ 
          color: "var(--color-text-secondary)", 
          textAlign: "center", 
          margin: 0,
          fontSize: "14px",
          lineHeight: "1.5",
          maxWidth: "400px"
        }}
      >
        {error}
      </p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="btn btn-primary"
          style={{
            marginTop: "8px",
            padding: "10px 20px",
            fontSize: "14px",
            fontWeight: "500",
          }}
        >
          🔄 Try Again
        </button>
      )}
    </div>
  );
};

export default ErrorMessage;
