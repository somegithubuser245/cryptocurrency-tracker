import {
  createChart,
  ChartOptions,
  DeepPartial,
  ColorType,
  CandlestickSeries,
  Background,
} from "lightweight-charts";
import { useEffect, useRef } from "react";
import type { KlineData } from "../types";

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
    const shitPriceFormatter = (p: number) => p.toFixed(4);

    const chartOptions: DeepPartial<ChartOptions> = {
      layout: {
        textColor: textColor ?? "white",
        background: background ?? { type: ColorType.Solid, color: "black" },
        fontFamily: "'Roboto', sans-serif",
        fontSize: 16,
      },
      grid: {
        vertLines: { color: "#444" },
        horzLines: { color: "#444" },
      },
      timeScale: {
        secondsVisible: true,
        timeVisible: true,
      },
      localization: {
        priceFormatter: shitPriceFormatter,
      },
      width: container.getBoundingClientRect().width,
      height: window.innerHeight / 3,
    };
    const chart = createChart(container, chartOptions);
    const candleStickSeries = chart.addSeries(CandlestickSeries);
    // Transform data to lightweight-charts format
    const transformedData = data.map((item) => ({
      time: Math.floor(item.time) as any, // Convert to seconds and cast to Time type
      open: item.open,
      high: item.high,
      low: item.low,
      close: item.close,
    }));

    candleStickSeries.setData(transformedData);

    const handleResize = () => {
      if (container) {
        chart.applyOptions({ width: container.getBoundingClientRect().width });
      }
    };

    chart.timeScale().fitContent();
    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      chart.remove();
    };
  }, [data, textColor, background]);

  return <div ref={containerRef} className="crypto_chart"></div>;
}

export default Chart;
