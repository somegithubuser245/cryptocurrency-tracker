import Chart from "./Chart";
import type { ChartCardProps } from "../types";

function ChartCard({ title, data }: ChartCardProps) {
  return (
    <div className="chart-card">
      <div className="chart-card-top-bar">
        <h2>{title}</h2>
      </div>
      <Chart data={data} />
    </div>
  );
}

export default ChartCard;
