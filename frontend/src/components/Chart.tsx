import {
  createChart,
  ChartOptions,
  DeepPartial,
  ColorType,
  CandlestickSeries,
  Background,
} from "lightweight-charts";
import { useEffect, useRef } from "react";

interface Props {
  data: any;
  textColor?: string;
  background?: DeepPartial<Background>;
}

function Chart({ data, textColor, background }: Props) {
  const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
      
      const chartOptions: DeepPartial<ChartOptions> = {
          layout: {
              textColor: textColor ?? "white",
              background: background ?? { type: ColorType.Solid, color: "black" },
            },
            width: containerRef.current?.getBoundingClientRect().width ?? 600,
            height: 300,
        };
        
        const chart = createChart(containerRef.current!, chartOptions);
        
        const candleStickSeries = chart.addSeries(CandlestickSeries);
        candleStickSeries.setData(data);
        
        const handleResize = () => {
            const container = containerRef.current
            if(container) {
                chart.applyOptions({ width: container.getBoundingClientRect().width });
            }
        };

        chart.timeScale().fitContent();
        window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      chart.remove();
    };
  }, [data]);

  return <div ref={containerRef}></div>;
}

export default Chart;
