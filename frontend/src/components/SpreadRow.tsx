import React, { useState } from "react";
import { useSpreadData } from "../hooks/useSpreadData";
import { formatCryptoPrice } from "../utils/priceFormatter";
import LoadingSpinner from "./LoadingSpinner";
import ErrorMessage from "./ErrorMessage";
import type { MaxSpreadResponse, AllSpreadsResponse } from "../types";

interface SpreadRowProps {
  pair: string;
  onClose: () => void;
}

const timeRanges = [
  { id: "5m", name: "5 minutes" },
  { id: "30m", name: "30 minutes" },
  { id: "1h", name: "Hourly" },
  { id: "4h", name: "4 Hours" },
  { id: "1d", name: "Daily" },
  { id: "1w", name: "Weekly" },
  { id: "1M", name: "Monthly" },
];

const SpreadRow: React.FC<SpreadRowProps> = ({ pair, onClose }) => {
  const [selectedTimeRange, setSelectedTimeRange] = useState("1h");
  const [showAllSpreads, setShowAllSpreads] = useState(false);
  const { maxSpreadData, allSpreadsData, loading, error, fetchSpreads } =
    useSpreadData();

  const handleFetchSpreads = async () => {
    await fetchSpreads({
      crypto_id: pair,
      interval: selectedTimeRange,
      api_provider: "binance", // Default to binance
    });
  };

  const formatSpread = (spread: number) => formatCryptoPrice(spread);
  const formatSpreadPercent = (percent: number) => `${percent.toFixed(4)}%`;
  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  return (
    <tr>
      <td colSpan={100} style={{ padding: 0, border: "none" }}>
        <div
          style={{
            backgroundColor: "var(--color-surface-light)",
            border: "1px solid var(--color-border)",
            borderRadius: "var(--border-radius)",
            margin: "8px",
            padding: "24px",
            boxShadow: "var(--shadow)",
          }}
        >
          {/* Header with close button */}
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: "20px",
            }}
          >
            <h3
              style={{
                margin: 0,
                color: "var(--color-text)",
                fontSize: "18px",
                fontWeight: "600",
              }}
            >
              📊 Spread Analysis for {pair}
            </h3>
            <button
              onClick={onClose}
              className="btn btn-secondary"
              style={{
                padding: "8px 12px",
                fontSize: "14px",
              }}
            >
              ✕ Close
            </button>
          </div>

          {/* Controls */}
          <div
            style={{
              display: "flex",
              gap: "16px",
              alignItems: "center",
              marginBottom: "20px",
              flexWrap: "wrap",
            }}
          >
            <div>
              <label
                style={{
                  display: "block",
                  marginBottom: "4px",
                  fontSize: "14px",
                  fontWeight: "500",
                  color: "var(--color-text)",
                }}
              >
                Time Range:
              </label>
              <select
                value={selectedTimeRange}
                onChange={(e) => setSelectedTimeRange(e.target.value)}
                className="input"
                style={{
                  padding: "8px 12px",
                  fontSize: "14px",
                  minWidth: "120px",
                }}
              >
                {timeRanges.map((range) => (
                  <option key={range.id} value={range.id}>
                    {range.name}
                  </option>
                ))}
              </select>
            </div>

            <div style={{ marginTop: "20px" }}>
              <button
                onClick={handleFetchSpreads}
                disabled={loading}
                className="btn btn-primary"
                style={{
                  padding: "10px 20px",
                  fontSize: "14px",
                  fontWeight: "500",
                }}
              >
                {loading ? "Loading..." : "🔍 Analyze Spreads"}
              </button>
            </div>
          </div>

          {/* Loading State */}
          {loading && (
            <div style={{ textAlign: "center", padding: "20px" }}>
              <LoadingSpinner message="Analyzing spreads..." />
            </div>
          )}

          {/* Error State */}
          {error && (
            <div style={{ marginBottom: "20px" }}>
              <ErrorMessage error={error} onRetry={handleFetchSpreads} />
            </div>
          )}

          {/* Results */}
          {maxSpreadData && !loading && (
            <div>
              {/* Max Spread Section */}
              <div
                style={{
                  backgroundColor: "var(--color-surface)",
                  border: "1px solid var(--color-border)",
                  borderRadius: "var(--border-radius)",
                  padding: "20px",
                  marginBottom: "16px",
                }}
              >
                <h4
                  style={{
                    margin: "0 0 16px 0",
                    color: "var(--color-text)",
                    fontSize: "16px",
                    fontWeight: "600",
                  }}
                >
                  🎯 Maximum Spread Found
                </h4>

                <div
                  style={{
                    display: "grid",
                    gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
                    gap: "16px",
                    fontSize: "14px",
                  }}
                >
                  <div>
                    <strong style={{ color: "var(--color-text)" }}>
                      Time:
                    </strong>
                    <div style={{ color: "var(--color-text-secondary)" }}>
                      {formatTimestamp(maxSpreadData.time)}
                    </div>
                  </div>
                  <div>
                    <strong style={{ color: "var(--color-text)" }}>
                      Spread:
                    </strong>
                    <div
                      style={{
                        color: "var(--color-success)",
                        fontWeight: "600",
                      }}
                    >
                      {formatSpread(maxSpreadData.spread)} (
                      {formatSpreadPercent(maxSpreadData.spread_percent)})
                    </div>
                  </div>
                  <div>
                    <strong style={{ color: "var(--color-text)" }}>
                      High Exchange:
                    </strong>
                    <div style={{ color: "var(--color-text-secondary)" }}>
                      {maxSpreadData.high_exchange}
                    </div>
                  </div>
                  <div>
                    <strong style={{ color: "var(--color-text)" }}>
                      Low Exchange:
                    </strong>
                    <div style={{ color: "var(--color-text-secondary)" }}>
                      {maxSpreadData.low_exchange}
                    </div>
                  </div>
                </div>
              </div>

              {/* All Spreads Section */}
              <div
                style={{
                  backgroundColor: "var(--color-surface)",
                  border: "1px solid var(--color-border)",
                  borderRadius: "var(--border-radius)",
                  padding: "20px",
                }}
              >
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    marginBottom: "12px",
                  }}
                >
                  <h4
                    style={{
                      margin: 0,
                      color: "var(--color-text)",
                      fontSize: "16px",
                      fontWeight: "600",
                    }}
                  >
                    📈 All Spreads Data
                  </h4>
                  <button
                    onClick={() => setShowAllSpreads(!showAllSpreads)}
                    className="btn btn-secondary"
                    style={{
                      padding: "6px 12px",
                      fontSize: "12px",
                    }}
                  >
                    {showAllSpreads ? "👆 Hide All" : "👇 Show All"}
                  </button>
                </div>

                {showAllSpreads && allSpreadsData && (
                  <div
                    style={{
                      maxHeight: "400px",
                      overflowY: "auto",
                      border: "1px solid var(--color-border)",
                      borderRadius: "var(--border-radius)",
                    }}
                  >
                    <table
                      style={{
                        width: "100%",
                        borderCollapse: "collapse",
                        fontSize: "13px",
                      }}
                    >
                      <thead
                        style={{
                          position: "sticky",
                          top: 0,
                          backgroundColor: "var(--color-surface-light)",
                        }}
                      >
                        <tr>
                          <th
                            style={{
                              padding: "12px",
                              textAlign: "left",
                              borderBottom: "1px solid var(--color-border)",
                              fontWeight: "600",
                              color: "var(--color-text)",
                            }}
                          >
                            Time
                          </th>
                          <th
                            style={{
                              padding: "12px",
                              textAlign: "right",
                              borderBottom: "1px solid var(--color-border)",
                              fontWeight: "600",
                              color: "var(--color-text)",
                            }}
                          >
                            Spread
                          </th>
                          <th
                            style={{
                              padding: "12px",
                              textAlign: "right",
                              borderBottom: "1px solid var(--color-border)",
                              fontWeight: "600",
                              color: "var(--color-text)",
                            }}
                          >
                            Spread %
                          </th>
                          <th
                            style={{
                              padding: "12px",
                              textAlign: "center",
                              borderBottom: "1px solid var(--color-border)",
                              fontWeight: "600",
                              color: "var(--color-text)",
                            }}
                          >
                            High Exchange
                          </th>
                          <th
                            style={{
                              padding: "12px",
                              textAlign: "center",
                              borderBottom: "1px solid var(--color-border)",
                              fontWeight: "600",
                              color: "var(--color-text)",
                            }}
                          >
                            Low Exchange
                          </th>
                        </tr>
                      </thead>
                      <tbody>
                        {Object.entries(allSpreadsData).map(
                          ([timestamp, data], index) => (
                            <tr
                              key={timestamp}
                              style={{
                                backgroundColor:
                                  index % 2 === 0
                                    ? "var(--color-surface)"
                                    : "var(--color-surface-light)",
                              }}
                            >
                              <td
                                style={{
                                  padding: "10px 12px",
                                  borderBottom: "1px solid var(--color-border)",
                                  color: "var(--color-text-secondary)",
                                }}
                              >
                                {formatTimestamp(timestamp)}
                              </td>
                              <td
                                style={{
                                  padding: "10px 12px",
                                  textAlign: "right",
                                  borderBottom: "1px solid var(--color-border)",
                                  color: "var(--color-text)",
                                  fontWeight: "500",
                                }}
                              >
                                {formatSpread(data.spread)}
                              </td>
                              <td
                                style={{
                                  padding: "10px 12px",
                                  textAlign: "right",
                                  borderBottom: "1px solid var(--color-border)",
                                  color: "var(--color-success)",
                                  fontWeight: "500",
                                }}
                              >
                                {formatSpreadPercent(data.spread_percent)}
                              </td>
                              <td
                                style={{
                                  padding: "10px 12px",
                                  textAlign: "center",
                                  borderBottom: "1px solid var(--color-border)",
                                  color: "var(--color-text-secondary)",
                                }}
                              >
                                {data.high_exchange}
                              </td>
                              <td
                                style={{
                                  padding: "10px 12px",
                                  textAlign: "center",
                                  borderBottom: "1px solid var(--color-border)",
                                  color: "var(--color-text-secondary)",
                                }}
                              >
                                {data.low_exchange}
                              </td>
                            </tr>
                          )
                        )}
                      </tbody>
                    </table>
                  </div>
                )}

                {!showAllSpreads && allSpreadsData && (
                  <p
                    style={{
                      margin: 0,
                      color: "var(--color-text-secondary)",
                      fontSize: "14px",
                    }}
                  >
                    {Object.keys(allSpreadsData).length} spread data points
                    available
                  </p>
                )}
              </div>
            </div>
          )}
        </div>
      </td>
    </tr>
  );
};

export default SpreadRow;
