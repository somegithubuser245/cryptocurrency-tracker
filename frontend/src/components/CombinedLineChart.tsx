import React, { useEffect, useRef, useState } from "react";
import {
  createChart,
  ChartOptions,
  DeepPartial,
  ColorType,
  LineStyle,
  LineSeries,
  MouseEventParams,
  Time,
} from "lightweight-charts";
import type { LineData } from "../types";
import {
  formatCryptoPrice,
  createSmartPriceFormatter,
} from "../utils/priceFormatter";
import { setupChartHandlers, createBaseChartOptions, CHART_DEFAULTS } from "../utils/chartUtils";

interface CombinedLineChartProps {
  data1: LineData[];
  data2: LineData[];
  exchange1Name: string;
  exchange2Name: string;
  pairName: string;
}

interface LegendValues {
  exchange1Value: number | null;
  exchange2Value: number | null;
}

const CombinedLineChart: React.FC<CombinedLineChartProps> = ({
  data1,
  data2,
  exchange1Name,
  exchange2Name,
  pairName,
}) => {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [legendValues, setLegendValues] = useState<LegendValues>({
    exchange1Value: null,
    exchange2Value: null,
  });

  // Helper function to find the closest data point to a given time
  const findValueAtTime = (
    data: LineData[],
    targetTime: number
  ): number | null => {
    if (!data.length) return null;

    // Find the closest time point
    let closest = data[0];
    let minDiff = Math.abs(closest.time - targetTime);

    for (const point of data) {
      const diff = Math.abs(point.time - targetTime);
      if (diff < minDiff) {
        minDiff = diff;
        closest = point;
      }
    }
    return closest.value;
  };

  // Initialize legend values with the last data points
  useEffect(() => {
    setLegendValues({
      exchange1Value: data1.length > 0 ? data1[data1.length - 1].value : null,
      exchange2Value: data2.length > 0 ? data2[data2.length - 1].value : null,
    });
  }, [data1, data2]);
  
  useEffect(() => {
    if (!containerRef.current || !data1.length || !data2.length) return;

    const container = containerRef.current;

    // Create smart price formatter based on all data
    const allPrices = [
      ...data1.map((d) => d.value),
      ...data2.map((d) => d.value),
    ];
    const smartFormatter = createSmartPriceFormatter(allPrices);

    // Use helper for base options and customize for line chart
    const baseOptions = createBaseChartOptions(false); // Light mode for line charts
    const chartOptions: DeepPartial<ChartOptions> = {
      ...baseOptions,
      layout: {
        ...baseOptions.layout,
        textColor: CHART_DEFAULTS.COLORS.TEXT_LIGHT,
        background: { type: ColorType.Solid, color: CHART_DEFAULTS.COLORS.BACKGROUND_LIGHT },
      },
      localization: {
        priceFormatter: smartFormatter,
      },
      width: container.getBoundingClientRect().width,
      height: CHART_DEFAULTS.SIZES.DEFAULT_HEIGHT,
    };

    const chart = createChart(container, chartOptions);
    
    // Add first exchange line series
    const lineSeries1 = chart.addSeries(LineSeries, {
      color: CHART_DEFAULTS.COLORS.LINE_BLUE,
      lineWidth: 2,
      lineStyle: LineStyle.Solid,
      title: exchange1Name,
    });

    // Add second exchange line series
    const lineSeries2 = chart.addSeries(LineSeries, {
      color: CHART_DEFAULTS.COLORS.LINE_ORANGE,
      lineWidth: 2,
      lineStyle: LineStyle.Solid,
      title: exchange2Name,
    });

    // Transform and set data
    const transformedData1 = data1.map((item) => ({
      time: Math.floor(item.time) as Time,
      value: item.value,
    }));

    const transformedData2 = data2.map((item) => ({
      time: Math.floor(item.time) as Time,
      value: item.value,
    }));
    
    lineSeries1.setData(transformedData1);
    lineSeries2.setData(transformedData2);

    // Subscribe to crosshair move for legend functionality
    chart.subscribeCrosshairMove((param: MouseEventParams) => {
      if (!param.time) {
        // Reset to last values when not hovering
        setLegendValues({
          exchange1Value:
            data1.length > 0 ? data1[data1.length - 1].value : null,
          exchange2Value:
            data2.length > 0 ? data2[data2.length - 1].value : null,
        });
        return;
      }

      const timeValue =
        typeof param.time === "number" ? param.time : Number(param.time);
      const value1 = findValueAtTime(data1, timeValue);
      const value2 = findValueAtTime(data2, timeValue);

      setLegendValues({
        exchange1Value: value1,
        exchange2Value: value2,
      });
    });

    // Use helper for chart handlers - ELIMINATES DUPLICATION
    const { cleanup } = setupChartHandlers(chart, container);

    // Return cleanup function
    return cleanup;
  }, [data1, data2, exchange1Name, exchange2Name]);

  return (
    <div className="chart-card">
      <div className="chart-card-top-bar">
        <h2>{pairName} - Line Comparison</h2>{" "}
        <div
          style={{
            marginLeft: "auto",
            display: "flex",
            gap: "15px",
            alignItems: "center",
          }}
        >
          <span style={{ display: "flex", alignItems: "center", gap: "5px" }}>
            <div
              style={{
                width: "12px",
                height: "2px",
                backgroundColor: CHART_DEFAULTS.COLORS.LINE_BLUE,
              }}
            />{" "}
            {exchange1Name}:{" "}
            {legendValues.exchange1Value !== null
              ? formatCryptoPrice(legendValues.exchange1Value)
              : data1.length > 0
              ? formatCryptoPrice(data1[data1.length - 1].value)
              : "N/A"}
          </span>
          <span style={{ display: "flex", alignItems: "center", gap: "5px" }}>
            <div
              style={{
                width: "12px",
                height: "2px",
                backgroundColor: CHART_DEFAULTS.COLORS.LINE_ORANGE,
              }}
            />
            {exchange2Name}:{" "}
            {legendValues.exchange2Value !== null
              ? formatCryptoPrice(legendValues.exchange2Value)
              : data2.length > 0
              ? formatCryptoPrice(data2[data2.length - 1].value)
              : "N/A"}
          </span>
        </div>
      </div>
      <div ref={containerRef} className="crypto_chart" />
    </div>
  );
};

export default CombinedLineChart;