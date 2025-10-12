import React, {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import { getComputedSpreads } from "../api/services";
import type { ComputedSpreadResponse } from "../types";
import LoadingSpinner from "./LoadingSpinner";

const clamp = (num: number, min: number, max: number) =>
  Math.min(Math.max(num, min), max);

const formatPercent = (value: number) => `${value.toFixed(2)}%`;

const formatTime = (iso: string | null) => {
  if (!iso) return "-";
  try {
    const d = new Date(iso);
    if (Number.isNaN(d.getTime())) return iso;
    return d.toLocaleString();
  } catch {
    return iso;
  }
};

const EmptyState: React.FC<{ message?: string }> = ({
  message = "No computed spreads yet.",
}) => (
  <div
    style={{
      textAlign: "center",
      padding: "24px",
      color: "var(--color-text-secondary)",
    }}
  >
    {message}
  </div>
);

/**
 * ComputedSpreadsTable
 * - Fetches /spreads/computed
 * - Polls at a configurable interval via slider (3s - 60s, default 10s)
 * - Shows loading, error, and last-updated indicator
 */
const ComputedSpreadsTable: React.FC = () => {
  const MIN_SEC = 3;
  const MAX_SEC = 60;
  const DEFAULT_SEC = 10;

  const [spreads, setSpreads] = useState<ComputedSpreadResponse[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [intervalSec, setIntervalSec] = useState<number>(DEFAULT_SEC);
  const [isFetching, setIsFetching] = useState<boolean>(false);
  const [isPaused, setIsPaused] = useState<boolean>(false);
  const [isExpanded, setIsExpanded] = useState<boolean>(false);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const intervalRef = useRef<number | null>(null);

  const fetchData = useCallback(async () => {
    setIsFetching(true);
    try {
      const data = await getComputedSpreads();
      setSpreads(data);
      setError(null);
      setLastUpdated(new Date());
    } catch (e) {
      const msg =
        e instanceof Error ? e.message : "Failed to fetch computed spreads";
      setError(msg);
      // keep old data visible if available
    } finally {
      setIsFetching(false);
    }
  }, []);

  // Kick off initial fetch and set up polling
  useEffect(() => {
    // Initial fetch on mount
    fetchData();

    // Clear any existing timer
    if (intervalRef.current) {
      window.clearInterval(intervalRef.current);
      intervalRef.current = null;
    }

    // Set up new interval based on intervalSec
    const id = window.setInterval(() => {
      // Skip background polling when tab is hidden or paused
      if (document.hidden || isPaused) return;
      fetchData();
    }, clamp(intervalSec, MIN_SEC, MAX_SEC) * 1000);
    intervalRef.current = id;

    return () => {
      if (intervalRef.current) {
        window.clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [fetchData, intervalSec, isPaused]);

  const handleSliderChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = Number(e.target.value);
    setIntervalSec(clamp(val, MIN_SEC, MAX_SEC));
  };

  const lastUpdatedLabel = useMemo(() => {
    if (!lastUpdated) return "";
    return `Last updated: ${lastUpdated.toLocaleTimeString()}`;
  }, [lastUpdated]);

  const DEFAULT_VISIBLE = 10;
  const visibleSpreads = useMemo(() => {
    if (!spreads) return null;
    return isExpanded ? spreads : spreads.slice(0, DEFAULT_VISIBLE);
  }, [spreads, isExpanded]);

  return (
    <div className="chart-card" style={{ marginTop: 0 }}>
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: 12,
          paddingBottom: 8,
          marginBottom: 12,
          borderBottom: "1px solid var(--color-border)",
        }}
      >
        <div>
          <h2 style={{ marginTop: 0, marginBottom: 4 }}>Computed Spreads</h2>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <div
              style={{
                width: 8,
                height: 8,
                borderRadius: "50%",
                backgroundColor: isFetching
                  ? "var(--color-warning)"
                  : "var(--color-success)",
              }}
              aria-label={isFetching ? "Fetching" : "Idle"}
              title={isFetching ? "Fetching" : "Idle"}
            />
            <span
              style={{ fontSize: 12, color: "var(--color-text-secondary)" }}
            >
              {lastUpdatedLabel || ""}
            </span>
            {spreads && (
              <span
                style={{ fontSize: 12, color: "var(--color-text-secondary)" }}
              >
                • {spreads.length} spreads
              </span>
            )}
            {spreads && spreads.length > DEFAULT_VISIBLE && (
              <span
                style={{ fontSize: 12, color: "var(--color-text-secondary)" }}
              >
                {isExpanded
                  ? "(showing all)"
                  : `(showing ${Math.min(DEFAULT_VISIBLE, spreads.length)})`}
              </span>
            )}
          </div>
        </div>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 12,
            flexWrap: "wrap",
          }}
        >
          {/* Expand/Collapse */}
          {spreads && spreads.length > DEFAULT_VISIBLE && (
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => setIsExpanded((x) => !x)}
              title={isExpanded ? "Show fewer rows" : "Show all rows"}
            >
              {isExpanded ? "Collapse" : "Expand"}
            </button>
          )}

          {/* Pause/Resume (orange for pause, green for resume) */}
          <button
            type="button"
            className="btn"
            onClick={() => setIsPaused((p) => !p)}
            aria-pressed={isPaused}
            title={isPaused ? "Resume auto-refresh" : "Pause auto-refresh"}
            style={{
              backgroundColor: isPaused
                ? "var(--color-success)" // Resume -> green
                : "var(--color-warning)", // Pause -> orange
              color: "#000",
              border: `1px solid ${
                isPaused ? "var(--color-success)" : "var(--color-warning)"
              }`,
            }}
          >
            {isPaused ? "Resume" : "Pause"}
          </button>

          {/* Refresh slider */}
          <label
            htmlFor="refreshInterval"
            style={{ fontSize: 14, color: "var(--color-text-secondary)" }}
          >
            Refresh: {intervalSec}s
          </label>
          <input
            id="refreshInterval"
            type="range"
            min={MIN_SEC}
            max={MAX_SEC}
            step={1}
            value={intervalSec}
            onChange={handleSliderChange}
            style={{ width: 160 }}
            aria-label="Refresh interval in seconds"
          />
        </div>
      </div>

      {isFetching && !spreads && (
        <LoadingSpinner message="Loading computed spreads..." />
      )}

      {error && !spreads && (
        <div
          style={{
            marginTop: 8,
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

      {spreads && spreads.length === 0 && <EmptyState />}

      {visibleSpreads && visibleSpreads.length > 0 && (
        <div style={{ overflowX: "auto" }}>
          <table
            style={{
              width: "100%",
              borderCollapse: "separate",
              borderSpacing: 0,
              border: "1px solid var(--color-border)",
              borderRadius: "var(--border-radius)",
              overflow: "hidden",
            }}
          >
            <thead style={{ backgroundColor: "var(--color-surface-light)" }}>
              <tr>
                <th
                  style={{
                    textAlign: "left",
                    padding: "12px 16px",
                    fontSize: 12,
                    color: "var(--color-text-secondary)",
                    borderBottom: "1px solid var(--color-border)",
                  }}
                >
                  #
                </th>
                <th
                  style={{
                    textAlign: "left",
                    padding: "12px 16px",
                    fontSize: 12,
                    color: "var(--color-text-secondary)",
                    borderBottom: "1px solid var(--color-border)",
                  }}
                >
                  Pair
                </th>
                <th
                  style={{
                    textAlign: "right",
                    padding: "12px 16px",
                    fontSize: 12,
                    color: "var(--color-text-secondary)",
                    borderBottom: "1px solid var(--color-border)",
                  }}
                >
                  Spread
                </th>
                <th
                  style={{
                    textAlign: "left",
                    padding: "12px 16px",
                    fontSize: 12,
                    color: "var(--color-text-secondary)",
                    borderBottom: "1px solid var(--color-border)",
                  }}
                >
                  Buy at
                </th>
                <th
                  style={{
                    textAlign: "left",
                    padding: "12px 16px",
                    fontSize: 12,
                    color: "var(--color-text-secondary)",
                    borderBottom: "1px solid var(--color-border)",
                  }}
                >
                  Sell at
                </th>
                <th
                  style={{
                    textAlign: "left",
                    padding: "12px 16px",
                    fontSize: 12,
                    color: "var(--color-text-secondary)",
                    borderBottom: "1px solid var(--color-border)",
                  }}
                >
                  Time
                </th>
              </tr>
            </thead>
            <tbody>
              {visibleSpreads.map((row, idx) => (
                <tr
                  key={`${row.crypto_name}-${row.high_exchange}-${row.low_exchange}-${idx}`}
                  style={{
                    backgroundColor:
                      idx % 2 ? "var(--color-surface)" : "transparent",
                  }}
                >
                  <td
                    style={{
                      padding: "12px 16px",
                      borderBottom: "1px solid var(--color-border)",
                      fontSize: 14,
                    }}
                  >
                    {idx + 1}
                  </td>
                  <td
                    style={{
                      padding: "12px 16px",
                      borderBottom: "1px solid var(--color-border)",
                      fontWeight: 600,
                    }}
                  >
                    {row.crypto_name}
                  </td>
                  <td
                    style={{
                      padding: "12px 16px",
                      borderBottom: "1px solid var(--color-border)",
                      textAlign: "right",
                      color: "var(--color-primary-light)",
                      fontWeight: 600,
                    }}
                  >
                    {formatPercent(row.spread_percent)}
                  </td>
                  <td
                    style={{
                      padding: "12px 16px",
                      borderBottom: "1px solid var(--color-border)",
                    }}
                  >
                    {row.low_exchange}
                  </td>
                  <td
                    style={{
                      padding: "12px 16px",
                      borderBottom: "1px solid var(--color-border)",
                    }}
                  >
                    {row.high_exchange}
                  </td>
                  <td
                    style={{
                      padding: "12px 16px",
                      borderBottom: "1px solid var(--color-border)",
                      color: "var(--color-text-secondary)",
                    }}
                  >
                    {formatTime(row.time)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {error && spreads && (
        <div
          style={{
            marginTop: 8,
            fontSize: 12,
            color: "var(--color-error)",
            textAlign: "right",
          }}
        >
          Last fetch error: {error}
        </div>
      )}
    </div>
  );
};

export default ComputedSpreadsTable;
