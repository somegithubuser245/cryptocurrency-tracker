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
        padding: "40px 20px",
        backgroundColor: "var(--color-surface)",
        border: "1px solid var(--color-border)",
        borderRadius: "var(--border-radius-lg)",
        margin: "20px",
        boxShadow: "var(--shadow)",
      }}
    >
      <div
        style={{
          fontSize: "48px",
          marginBottom: "16px",
          color: "var(--color-error)",
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
          fontSize: "14px", 
          textAlign: "center", 
          margin: "0 0 16px 0",
          maxWidth: "400px",
          lineHeight: "1.4",
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