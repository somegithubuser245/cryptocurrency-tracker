import React from "react";

interface LoadingSpinnerProps {
  message?: string;
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  message = "Loading...",
}) => {
  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: "40px 20px",
        gap: "16px",
        minHeight: "200px",
      }}
    >
      <div
        style={{
          border: "3px solid var(--color-surface-light)",
          borderTop: "3px solid var(--color-primary)",
          borderRadius: "50%",
          width: "48px",
          height: "48px",
          animation: "spin 1s linear infinite",
        }}
      />
      <p 
        style={{ 
          margin: 0,
          color: "var(--color-text-secondary)",
          fontSize: "14px",
          fontWeight: "500"
        }}
      >
        {message}
      </p>
      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default LoadingSpinner;
