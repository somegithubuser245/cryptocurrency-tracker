import React, { useState, useEffect } from 'react';
import { XAxis, YAxis, ResponsiveContainer, Tooltip, Legend, ComposedChart, Bar } from 'recharts';
import axios from 'axios';

const CryptoTracker = () => {
  const [selectedCrypto, setSelectedCrypto] = useState('bitcoin');
  const [candleData, setCandleData] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [timeframe, setTimeframe] = useState('7');
  const [yDomain, setYDomain] = useState([0, 0]);

  const fetchOHLCData = async (cryptoId, days) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await axios.get(`http://localhost:8000/api/crypto/${cryptoId}/ohlc?days=${days}`);
      
      // Process the data with improved calculations
      const processedData = response.data.map(candle => ({
        ...candle,
        bodyHeight: Math.abs(candle.close - candle.open),
        bodyStart: Math.min(candle.open, candle.close),
        wickHeight: candle.high - candle.low,
        wickStart: candle.low,
        color: candle.close >= candle.open ? '#16a34a' : '#dc2626'
      }));

      // Calculate domain with nice round numbers
      const yMin = Math.min(...processedData.map(d => d.low));
      const yMax = Math.max(...processedData.map(d => d.high));
      
      setYDomain([yMin, yMax]);
      setCandleData(processedData);
    } catch (error) {
      console.error('Error fetching OHLC data:', error);
      setError('Failed to load OHLC data');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchOHLCData(selectedCrypto, timeframe);
  }, [selectedCrypto, timeframe]);

  const CustomCandlestick = (props) => {
    const { x, y, width, height, payload } = props;
    if (!payload) return null;

    // Calculate relative positions within the chart
    const totalRange = yDomain[1] - yDomain[0];
    const wickBottom = ((payload.low - yDomain[0]) / totalRange) * height;
    const wickTop = ((payload.high - yDomain[0]) / totalRange) * height;
    const bodyBottom = ((payload.bodyStart - yDomain[0]) / totalRange) * height;
    const bodyTop = ((payload.bodyStart + payload.bodyHeight - yDomain[0]) / totalRange) * height;

    return (
      <g>
        {/* Wick line */}
        <line
          x1={x + width / 2}
          y1={height - wickBottom}
          x2={x + width / 2}
          y2={height - wickTop}
          stroke={payload.color}
          strokeWidth={1}
        />
        {/* Body rectangle */}
        <rect
          x={x + width * 0.25}
          y={height - bodyTop}
          width={width * 0.5}
          height={Math.abs(bodyTop - bodyBottom)}
          fill={payload.color}
        />
      </g>
    );
  };

  return (
    <div className="w-full h-screen p-4">
      <div className="h-full bg-white rounded-lg shadow-lg">
        <div className="p-4 border-b">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-bold text-gray-800">Crypto OHLC Chart</h2>
            <div className="flex gap-4">
              <select
                value={timeframe}
                onChange={(e) => setTimeframe(e.target.value)}
                className="px-4 py-2 border rounded-md bg-white shadow-sm"
              >
                <option value="1">24 Hours</option>
                <option value="7">7 Days</option>
                <option value="30">30 Days</option>
              </select>
              <select
                value={selectedCrypto}
                onChange={(e) => setSelectedCrypto(e.target.value)}
                className="px-4 py-2 border rounded-md bg-white shadow-sm"
              >
                <option value="bitcoin">Bitcoin</option>
                <option value="ethereum">Ethereum</option>
              </select>
            </div>
          </div>
        </div>

        <div className="p-4 h-[calc(100%-5rem)]">
          {isLoading ? (
            <div className="h-full flex items-center justify-center">
              <div className="text-gray-600">Loading...</div>
            </div>
          ) : error ? (
            <div className="text-red-500 text-center">{error}</div>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart
                data={candleData}
                margin={{ top: 10, right: 30, left: 70, bottom: 30 }}
              >
                <XAxis
                  dataKey="timestamp"
                  tickFormatter={(value) => new Date(value).toLocaleDateString()}
                  height={50}
                />
                <YAxis
                  type="number"
                  domain={[90000, 100000]}
                  tickFormatter={(value) => `${value.toLocaleString()}`}
                  width={60}
                  scale="linear"
                  interval={0}
                  allowDataOverflow={false}
                />
                <Tooltip
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const data = payload[0].payload;
                      return (
                        <div className="bg-white p-2 border rounded shadow">
                          <p>Time: {new Date(data.timestamp).toLocaleString()}</p>
                          <p>Open: ${data.open.toLocaleString()}</p>
                          <p>High: ${data.high.toLocaleString()}</p>
                          <p>Low: ${data.low.toLocaleString()}</p>
                          <p>Close: ${data.close.toLocaleString()}</p>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Bar
                  dataKey="wickHeight"
                  shape={<CustomCandlestick />}
                  isAnimationActive={false}
                />
              </ComposedChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>
    </div>
  );
};

export default CryptoTracker;