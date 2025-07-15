import {
  createChart,
  ChartOptions,
  DeepPartial,
  ColorType,
  CandlestickSeries,
  Background,
  Time,
} from "lightweight-charts";
import { useEffect, useRef } from "react";
import type { KlineData } from "../types";
import { createSmartPriceFormatter } from "../utils/priceFormatter";
import { setupChartHandlers, createBaseChartOptions, CHART_DEFAULTS } from "../utils/chartUtils";

interface ChartProps {
  data: KlineData[];
  textColor?: string;
  background?: DeepPartial<Background>;
}

function Chart({ data, textColor, background }: ChartProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  
  useEffect(() => {
    if (!containerRef.current || !data) return;

    const container = containerRef.current;

    // Extract all price values for smart formatting
    const allPrices = data.flatMap((candle) => [
      candle.open,
      candle.high,
      candle.low,
      candle.close,
    ]);
    const smartPriceFormatter = createSmartPriceFormatter(allPrices);

    // Use helper for base options and customize for candlestick chart
    const baseOptions = createBaseChartOptions(true); // Dark mode for OHLC
    const chartOptions: DeepPartial<ChartOptions> = {
      ...baseOptions,
      layout: {
        ...baseOptions.layout,
        textColor: textColor ?? CHART_DEFAULTS.COLORS.TEXT_DARK,
        background: background ?? { type: ColorType.Solid, color: CHART_DEFAULTS.COLORS.BACKGROUND_DARK },
        fontSize: CHART_DEFAULTS.SIZES.FONT_SIZE_LARGE,
      },
      localization: {
        priceFormatter: smartPriceFormatter,
      },
      width: container.getBoundingClientRect().width,
      height: window.innerHeight / 3,
    };

    const chart = createChart(container, chartOptions);
    const candleStickSeries = chart.addSeries(CandlestickSeries);
    
    // Transform data to lightweight-charts format
    const transformedData = data.map((item) => ({
      time: Math.floor(item.time) as Time,
      open: item.open,
      high: item.high,
      low: item.low,
      close: item.close,
    }));

    candleStickSeries.setData(transformedData);

    // Use helper for chart handlers - ELIMINATES DUPLICATION
    const { cleanup } = setupChartHandlers(chart, container);

    // Return cleanup function
    return cleanup;
  }, [data, textColor, background]);

  return <div ref={containerRef} className="crypto_chart"></div>;
}

export default Chart;