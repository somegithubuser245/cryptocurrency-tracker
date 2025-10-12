import { useEffect, useState } from "react";
import "./App.css";
import { initializeAndComputeSpreads, getBatchStatus } from "./api/services";
import type { BatchStatusSummaryResponse } from "./types";
import ComputedSpreadsTable from "./components/ComputedSpreadsTable";

function App() {
  const [batchStatus, setBatchStatus] =
    useState<BatchStatusSummaryResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isBackendConnected, setIsBackendConnected] = useState(false);

  // Fetch batch status every 3 seconds
  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const status = await getBatchStatus();
        console.log("Fetched batch status:", status);
        setBatchStatus(status);
        setIsBackendConnected(true);
        setError(null);
      } catch (err) {
        console.error("Failed to fetch status:", err);
        setIsBackendConnected(false);
        // Don't clear existing status on error, just log it
      }
    };

    // Initial fetch
    fetchStatus();

    // Poll every 3 seconds
    const interval = setInterval(fetchStatus, 3000);

    return () => clearInterval(interval);
  }, []);

  const handleStartComputation = async () => {
    setIsLoading(true);
    setError(null);

    try {
      await initializeAndComputeSpreads();
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to start computation"
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app">
      <div className="controls-bar">
        <h1 style={{ margin: 0, fontSize: "1.75rem" }}>
          Cryptocurrency Tracker
        </h1>
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <div
            style={{
              width: "8px",
              height: "8px",
              borderRadius: "50%",
              backgroundColor: isBackendConnected
                ? "var(--color-success)"
                : "var(--color-error)",
            }}
          />
          <span
            style={{
              fontSize: "0.875rem",
              color: "var(--color-text-secondary)",
            }}
          >
            {isBackendConnected ? "Connected" : "Backend Disconnected"}
          </span>
        </div>
      </div>

      <div style={{ padding: "24px", maxWidth: "1200px", margin: "0 auto" }}>
        {/* Backend Connection Warning */}
        {!isBackendConnected && (
          <div
            style={{
              marginBottom: "24px",
              marginTop: 0,
              padding: "16px",
              backgroundColor: "rgba(239, 68, 68, 0.1)",
              color: "var(--color-error)",
              borderRadius: "var(--border-radius)",
              border: "1px solid var(--color-error)",
            }}
          >
            <strong>⚠️ Backend Not Connected</strong>
            <p style={{ margin: "8px 0 0 0" }}>
              Cannot connect to the backend API at{" "}
              <code>http://127.0.0.1:8000</code>. Please ensure the backend
              server is running.
            </p>
          </div>
        )}

        {/* Control Section */}
        <div
          className="chart-card"
          style={{ marginBottom: "24px", marginTop: 0 }}
        >
          <h2 style={{ marginTop: 0, marginBottom: "16px" }}>
            Spread Computation
          </h2>

          <button
            onClick={handleStartComputation}
            disabled={isLoading}
            className={`btn ${isLoading ? "btn-secondary" : "btn-primary"}`}
          >
            {isLoading ? "Starting..." : "Start Spread Computation"}
          </button>

          {error && (
            <div
              style={{
                marginTop: "16px",
                padding: "12px 16px",
                backgroundColor: "rgba(239, 68, 68, 0.1)",
                color: "var(--color-error)",
                borderRadius: "var(--border-radius)",
                border: "1px solid var(--color-error)",
              }}
            >
              {error}
            </div>
          )}
        </div>

        {/* Batch Status Section */}
        <div className="chart-card" style={{ marginTop: 0 }}>
          <h2 style={{ marginTop: 0, marginBottom: "20px" }}>
            Batch Processing Status
          </h2>

          {batchStatus ? (
            <>
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
                  gap: "16px",
                  marginBottom: "20px",
                }}
              >
                <div
                  style={{
                    padding: "16px",
                    backgroundColor: "var(--color-surface-light)",
                    borderRadius: "var(--border-radius)",
                    border: "1px solid var(--color-border)",
                  }}
                >
                  <div
                    style={{
                      fontSize: "0.875rem",
                      color: "var(--color-text-secondary)",
                      marginBottom: "8px",
                    }}
                  >
                    Total Pairs
                  </div>
                  <div
                    style={{
                      fontSize: "2rem",
                      fontWeight: "600",
                      color: "var(--color-primary-light)",
                    }}
                  >
                    {batchStatus.total_pairs}
                  </div>
                </div>

                <div
                  style={{
                    padding: "16px",
                    backgroundColor: "var(--color-surface-light)",
                    borderRadius: "var(--border-radius)",
                    border: "1px solid var(--color-border)",
                  }}
                >
                  <div
                    style={{
                      fontSize: "0.875rem",
                      color: "var(--color-text-secondary)",
                      marginBottom: "8px",
                    }}
                  >
                    Cached
                  </div>
                  <div
                    style={{
                      fontSize: "2rem",
                      fontWeight: "600",
                      color: "var(--color-success)",
                    }}
                  >
                    {batchStatus.cached}
                  </div>
                </div>

                <div
                  style={{
                    padding: "16px",
                    backgroundColor: "var(--color-surface-light)",
                    borderRadius: "var(--border-radius)",
                    border: "1px solid var(--color-border)",
                  }}
                >
                  <div
                    style={{
                      fontSize: "0.875rem",
                      color: "var(--color-text-secondary)",
                      marginBottom: "8px",
                    }}
                  >
                    Spreads Computed
                  </div>
                  <div
                    style={{
                      fontSize: "2rem",
                      fontWeight: "600",
                      color: "var(--color-primary)",
                    }}
                  >
                    {batchStatus.spreads_computed}
                  </div>
                </div>

                <div
                  style={{
                    padding: "16px",
                    backgroundColor: "var(--color-surface-light)",
                    borderRadius: "var(--border-radius)",
                    border: "1px solid var(--color-border)",
                  }}
                >
                  <div
                    style={{
                      fontSize: "0.875rem",
                      color: "var(--color-text-secondary)",
                      marginBottom: "8px",
                    }}
                  >
                    Progress
                  </div>
                  <div
                    style={{
                      fontSize: "2rem",
                      fontWeight: "600",
                      color: "var(--color-warning)",
                    }}
                  >
                    {batchStatus.processing_progress.toFixed(1)}%
                  </div>
                </div>
              </div>

              {/* Progress Bar */}
              <div
                style={{
                  width: "100%",
                  height: "8px",
                  backgroundColor: "var(--color-surface-light)",
                  borderRadius: "4px",
                  overflow: "hidden",
                  border: "1px solid var(--color-border)",
                }}
              >
                <div
                  style={{
                    width: `${batchStatus.processing_progress}%`,
                    height: "100%",
                    backgroundColor: "var(--color-primary)",
                    transition: "width 0.5s ease",
                  }}
                />
              </div>
            </>
          ) : (
            <div
              style={{
                textAlign: "center",
                padding: "40px",
                color: "var(--color-text-secondary)",
              }}
            >
              Loading batch status...
            </div>
          )}
        </div>

        {/* Computed Spreads Table */}
        <ComputedSpreadsTable />
      </div>
    </div>
  );
}

export default App;
