import React, { useState, useMemo } from "react";
import type { PairsExchangesResponse } from "../types";
import LoadingSpinner from "./LoadingSpinner";
import ErrorMessage from "./ErrorMessage";
import SpreadRow from "./SpreadRow";

interface PairsTableProps {
  pairsData: PairsExchangesResponse | null;
  loading: boolean;
  error: string | null;
  onRetry: () => void;
}

const PairsTable: React.FC<PairsTableProps> = ({
  pairsData,
  loading,
  error,
  onRetry,
}) => {
  const [searchTerm, setSearchTerm] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [expandedRow, setExpandedRow] = useState<string | null>(null);
  const itemsPerPage = 50;

  // Filter pairs based on search term
  const filteredPairs = useMemo(() => {
    if (!pairsData) return [];

    const pairs = Object.keys(pairsData);
    if (!searchTerm) return pairs;

    return pairs.filter((pair) =>
      pair.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [pairsData, searchTerm]);

  // Paginate filtered pairs
  const paginatedPairs = useMemo(() => {
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    return filteredPairs.slice(startIndex, endIndex);
  }, [filteredPairs, currentPage]);

  const totalPages = Math.ceil(filteredPairs.length / itemsPerPage);

  // Get all unique exchanges from the data
  const allExchanges = useMemo(() => {
    if (!pairsData) return [];

    const exchangeSet = new Set<string>();
    Object.values(pairsData).forEach((exchangeList) => {
      exchangeList.forEach((exchange) => exchangeSet.add(exchange));
    });

    return Array.from(exchangeSet).sort();
  }, [pairsData]);

  if (loading) {
    return <LoadingSpinner message="Loading pairs data..." />;
  }

  if (error) {
    return <ErrorMessage error={error} onRetry={onRetry} />;
  }

  if (!pairsData) {
    return (
      <div style={{ padding: "20px", textAlign: "center" }}>
        No data available
      </div>
    );
  }

  return (
    <div
      style={{
        padding: "24px",
        backgroundColor: "var(--color-background)",
        minHeight: "100vh",
      }}
    >
      <div style={{ marginBottom: "24px" }}>
        <h2
          style={{
            margin: "0 0 8px 0",
            color: "var(--color-text)",
            fontSize: "28px",
            fontWeight: "600",
          }}
        >
          📋 Exchange Support Matrix
        </h2>
        <p
          style={{
            margin: "0 0 20px 0",
            color: "var(--color-text-secondary)",
            fontSize: "14px",
          }}
        >
          Find which exchanges support your favorite cryptocurrency pairs
        </p>

        {/* Search Bar */}
        <div style={{ marginBottom: "20px" }}>
          <input
            type="text"
            placeholder="🔍 Search pairs (e.g., BTC, ETH, USDT)..."
            value={searchTerm}
            onChange={(e) => {
              setSearchTerm(e.target.value);
              setCurrentPage(1); // Reset to first page when searching
            }}
            className="input"
            style={{
              width: "100%",
              maxWidth: "500px",
              padding: "12px 16px",
              fontSize: "14px",
            }}
          />
        </div>

        {/* Stats */}
        <div
          style={{
            display: "flex",
            gap: "24px",
            marginBottom: "24px",
            fontSize: "13px",
            color: "var(--color-text-secondary)",
            flexWrap: "wrap",
          }}
        >
          <div
            style={{
              padding: "8px 12px",
              backgroundColor: "var(--color-surface)",
              borderRadius: "var(--border-radius)",
              border: "1px solid var(--color-border)",
            }}
          >
            📊 <strong>{filteredPairs.length}</strong> pairs
          </div>
          <div
            style={{
              padding: "8px 12px",
              backgroundColor: "var(--color-surface)",
              borderRadius: "var(--border-radius)",
              border: "1px solid var(--color-border)",
            }}
          >
            🏪 <strong>{allExchanges.length}</strong> exchanges
          </div>
          {searchTerm && (
            <div
              style={{
                padding: "8px 12px",
                backgroundColor: "var(--color-primary)",
                color: "white",
                borderRadius: "var(--border-radius)",
              }}
            >
              Filtered from <strong>{Object.keys(pairsData).length}</strong>{" "}
              total pairs
            </div>
          )}
        </div>
      </div>

      {/* Table Container with Horizontal Scroll */}
      <div
        style={{
          overflowX: "auto",
          overflowY: "auto",
          maxHeight: "70vh",
          border: "1px solid var(--color-border)",
          borderRadius: "var(--border-radius-lg)",
          backgroundColor: "var(--color-surface)",
          boxShadow: "var(--shadow)",
        }}
      >
        <table
          style={{
            width: "100%",
            borderCollapse: "collapse",
            minWidth: `${Math.max(
              600,
              allExchanges.length * 100 + 200 + 120
            )}px`,
          }}
        >
          <thead style={{ position: "sticky", top: 0, zIndex: 20 }}>
            <tr style={{ backgroundColor: "var(--color-surface-light)" }}>
              <th
                style={{
                  padding: "16px",
                  textAlign: "left",
                  fontWeight: "600",
                  color: "var(--color-text)",
                  borderBottom: "2px solid var(--color-border)",
                  position: "sticky",
                  left: 0,
                  backgroundColor: "var(--color-surface-light)",
                  zIndex: 21,
                  minWidth: "150px",
                  fontSize: "14px",
                  boxShadow: "2px 0 4px rgba(0,0,0,0.2)",
                }}
              >
                Cryptocurrency Pair
              </th>
              {allExchanges.map((exchange) => (
                <th
                  key={exchange}
                  style={{
                    padding: "16px 12px",
                    textAlign: "center",
                    fontWeight: "600",
                    color: "var(--color-text)",
                    borderBottom: "2px solid var(--color-border)",
                    borderLeft: "1px solid var(--color-border)",
                    minWidth: "90px",
                    fontSize: "12px",
                    textTransform: "capitalize",
                    backgroundColor: "var(--color-surface-light)",
                  }}
                >
                  {exchange}
                </th>
              ))}
              <th
                style={{
                  padding: "16px 12px",
                  textAlign: "center",
                  fontWeight: "600",
                  color: "var(--color-text)",
                  borderBottom: "2px solid var(--color-border)",
                  borderLeft: "1px solid var(--color-border)",
                  minWidth: "120px",
                  fontSize: "12px",
                  backgroundColor: "var(--color-surface-light)",
                }}
              >
                Spread Analysis
              </th>
            </tr>
          </thead>
          <tbody>
            {paginatedPairs.map((pair, index) => (
              <React.Fragment key={pair}>
                <tr
                  style={{
                    backgroundColor:
                      index % 2 === 0
                        ? "var(--color-surface)"
                        : "var(--color-surface-light)",
                    transition: "background-color 0.2s ease",
                  }}
                >
                  <td
                    style={{
                      padding: "14px 16px",
                      fontWeight: "600",
                      color: "var(--color-text)",
                      borderBottom: "1px solid var(--color-border)",
                      position: "sticky",
                      left: 0,
                      backgroundColor:
                        index % 2 === 0
                          ? "var(--color-surface)"
                          : "var(--color-surface-light)",
                      zIndex: 5,
                      fontSize: "14px",
                      boxShadow: "2px 0 4px rgba(0,0,0,0.2)",
                    }}
                  >
                    {pair}
                  </td>
                  {allExchanges.map((exchange) => {
                    const isSupported = pairsData[pair]?.includes(exchange);
                    return (
                      <td
                        key={exchange}
                        style={{
                          padding: "14px 12px",
                          textAlign: "center",
                          borderBottom: "1px solid var(--color-border)",
                          borderLeft: "1px solid var(--color-border)",
                        }}
                      >
                        <span
                          style={{
                            display: "inline-flex",
                            alignItems: "center",
                            justifyContent: "center",
                            width: "24px",
                            height: "24px",
                            borderRadius: "50%",
                            backgroundColor: isSupported
                              ? "var(--color-success)"
                              : "var(--color-surface-light)",
                            color: isSupported
                              ? "#ffffff"
                              : "var(--color-text-secondary)",
                            fontSize: "12px",
                            fontWeight: "bold",
                            border: isSupported
                              ? "none"
                              : "1px solid var(--color-border)",
                          }}
                        >
                          {isSupported ? "✓" : "✗"}
                        </span>
                      </td>
                    );
                  })}
                  <td
                    style={{
                      padding: "14px 12px",
                      textAlign: "center",
                      borderBottom: "1px solid var(--color-border)",
                      borderLeft: "1px solid var(--color-border)",
                    }}
                  >
                    <button
                      onClick={() =>
                        setExpandedRow(expandedRow === pair ? null : pair)
                      }
                      className="btn btn-primary"
                      style={{
                        padding: "6px 12px",
                        fontSize: "12px",
                        fontWeight: "500",
                      }}
                    >
                      {expandedRow === pair ? "📈 Hide" : "📊 Get Spreads"}
                    </button>
                  </td>
                </tr>
                {expandedRow === pair && (
                  <SpreadRow
                    pair={pair}
                    onClose={() => setExpandedRow(null)}
                  />
                )}
              </React.Fragment>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div
          style={{
            marginTop: "24px",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            gap: "12px",
          }}
        >
          <button
            onClick={() => setCurrentPage((prev) => Math.max(1, prev - 1))}
            disabled={currentPage === 1}
            className={`btn ${
              currentPage === 1 ? "btn-secondary" : "btn-primary"
            }`}
            style={{
              opacity: currentPage === 1 ? 0.5 : 1,
              cursor: currentPage === 1 ? "not-allowed" : "pointer",
            }}
          >
            ← Previous
          </button>

          <div
            style={{
              padding: "8px 16px",
              backgroundColor: "var(--color-surface)",
              borderRadius: "var(--border-radius)",
              border: "1px solid var(--color-border)",
              color: "var(--color-text)",
              fontSize: "14px",
              fontWeight: "500",
            }}
          >
            Page <strong>{currentPage}</strong> of <strong>{totalPages}</strong>
          </div>

          <button
            onClick={() =>
              setCurrentPage((prev) => Math.min(totalPages, prev + 1))
            }
            disabled={currentPage === totalPages}
            className={`btn ${
              currentPage === totalPages ? "btn-secondary" : "btn-primary"
            }`}
            style={{
              opacity: currentPage === totalPages ? 0.5 : 1,
              cursor: currentPage === totalPages ? "not-allowed" : "pointer",
            }}
          >
            Next →
          </button>
        </div>
      )}

      {filteredPairs.length === 0 && searchTerm && (
        <div
          style={{
            textAlign: "center",
            padding: "60px 20px",
            color: "var(--color-text-secondary)",
            fontSize: "16px",
            backgroundColor: "var(--color-surface)",
            borderRadius: "var(--border-radius-lg)",
            border: "1px solid var(--color-border)",
            marginTop: "24px",
          }}
        >
          <div style={{ fontSize: "48px", marginBottom: "16px" }}>🔍</div>
          <div style={{ fontWeight: "500", marginBottom: "8px" }}>
            No pairs found
          </div>
          <div>No cryptocurrency pairs match "{searchTerm}"</div>
        </div>
      )}
    </div>
  );
};

export default PairsTable;
