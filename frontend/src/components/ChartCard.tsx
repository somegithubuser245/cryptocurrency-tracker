import Chart from "./Chart";

interface Props {
  title: string;
  data: any;
  api_provider: string;
}

function ChartCard({ title, data, api_provider }: Props) {
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
