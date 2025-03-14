import { useState } from "react";
import Chart from "./Chart";

interface Props {
  data: any;
  cryptoPairs: Array<{ id: string; name: string }>;
  timeRanges: Array<{ id: string; name: string }>;
}

function ChartCard({ data, cryptoPairs, timeRanges }: Props) {
  const [cryptoIndex, setCryptoIndex] = useState(0);
  const [timeRangeIndex, setTimeRangeIndex] = useState(0);

  return (
    <>
      <div className="chart-card">
        <div className="chart-card-top-bar">
          <h2>{cryptoPairs[cryptoIndex].name}</h2>
          <div className="card-dropdown">
            <select name="Crypto">
              {cryptoPairs.map((cryptoPair, index) => (
                <option
                  value={cryptoPair.name}
                  key={cryptoPair.id}
                  onClick={() => setCryptoIndex(index)}
                >
                  {cryptoPair.name}
                </option>
              ))}
            </select>
          </div>
          <div className="card-dropdown">
            <select name="Ranges">
              {timeRanges.map((timeRange, index) => (
                <option
                  value={timeRange.name}
                  key={timeRange.id}
                  onClick={() => setTimeRangeIndex(index)}
                >
                  {timeRange.name}
                </option>
              ))}
            </select>
          </div>
        </div>
        <Chart data={data}></Chart>
      </div>
    </>
  );
}

export default ChartCard;
