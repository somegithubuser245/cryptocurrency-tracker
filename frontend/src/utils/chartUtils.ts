/**
 * Chart utilities to eliminate duplicated code between Chart.tsx and CombinedLineChart.tsx
 */
import { IChartApi } from "lightweight-charts";

export interface ChartCleanupResult {
  handleResize: () => void;
  cleanup: () => void;
}

/**
 * Sets up chart resize handling and cleanup logic
 * Eliminates duplication between Chart.tsx and CombinedLineChart.tsx
 * 
 * @param chart - The lightweight chart instance
 * @param container - The container HTML element
 * @returns Object with handleResize function and cleanup function
 */
export function setupChartHandlers(
  chart: IChartApi, 
  container: HTMLElement
): ChartCleanupResult {
  
  // Create resize handler
  const handleResize = () => {
    if (container) {
      chart.applyOptions({ width: container.getBoundingClientRect().width });
    }
  };

  // Setup initial chart state
  chart.timeScale().fitContent();
  window.addEventListener("resize", handleResize);

  // Create cleanup function
  const cleanup = () => {
    window.removeEventListener("resize", handleResize);
    chart.remove();
  };

  return {
    handleResize,
    cleanup
  };
}

/**
 * Common chart configuration options
 */
export const CHART_DEFAULTS = {
  FONT_FAMILY: "'Roboto', sans-serif",
  RESIZE_DEBOUNCE_MS: 100,
  
  COLORS: {
    GRID_LIGHT: "#f0f0f0",
    GRID_DARK: "#444",
    TEXT_LIGHT: "#333", 
    TEXT_DARK: "white",
    BACKGROUND_LIGHT: "#ffffff",
    BACKGROUND_DARK: "black",
    
    // Line colors for consistency
    LINE_BLUE: "#2196F3",
    LINE_ORANGE: "#FF9800",
  },
  
  SIZES: {
    DEFAULT_HEIGHT: 400,
    FONT_SIZE: 14,
    FONT_SIZE_LARGE: 16,
  }
} as const;

/**
 * Helper to create consistent chart options
 */
export function createBaseChartOptions(isDark: boolean = false) {
  return {
    layout: {
      fontFamily: CHART_DEFAULTS.FONT_FAMILY,
      fontSize: CHART_DEFAULTS.SIZES.FONT_SIZE,
    },
    grid: {
      vertLines: { 
        color: isDark ? CHART_DEFAULTS.COLORS.GRID_DARK : CHART_DEFAULTS.COLORS.GRID_LIGHT 
      },
      horzLines: { 
        color: isDark ? CHART_DEFAULTS.COLORS.GRID_DARK : CHART_DEFAULTS.COLORS.GRID_LIGHT 
      },
    },
    timeScale: {
      timeVisible: true,
      secondsVisible: isDark, // Show seconds in dark mode (candlestick charts)
    },
  };
}