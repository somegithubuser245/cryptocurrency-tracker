import React, { useEffect, useRef, useState } from 'react';
import { createChart } from 'lightweight-charts';

const CRYPTO_OPTIONS = [
  { id: 'bitcoin', name: 'Bitcoin' },
  { id: 'ethereum', name: 'Ethereum' },
  { id: 'solana', name: 'Solana' },
  { id: 'dogecoin', name: 'Dogecoin' },
  { id: 'cardano', name: 'Cardano' }
];

const TIME_RANGES = [
  { value: '1', label: '24 Hours' },
  { value: '7', label: '7 Days' },
  { value: '30', label: '30 Days' },
  { value: '90', label: '90 Days' }
];

const CryptoChart = () => {
  const chartContainerRef = useRef();
  const chart = useRef();
  const [selectedCrypto, setSelectedCrypto] = useState('bitcoin');
  const [timeRange, setTimeRange] = useState('7');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Create chart instance
    chart.current = createChart(chartContainerRef.current, {
      layout: {
        background: { color: '#ffffff' },
        textColor: '#333',
      },
      width: chartContainerRef.current.clientWidth,
      height: 500,
      timeScale: {
        timeVisible: true,
        secondsVisible: false,
      },
      crosshair: {
        mode: 1
      },
      grid: {
        vertLines: { color: '#f0f0f0' },
        horzLines: { color: '#f0f0f0' },
      },
    });

    // Create candlestick series
    const candlestickSeries = chart.current.addCandlestickSeries({
      upColor: '#16a34a',
      downColor: '#dc2626',
      borderVisible: false,
      wickUpColor: '#16a34a',
      wickDownColor: '#dc2626',
    });

    // Add data
    const fetchData = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const response = await fetch(`http://localhost:8000/api/crypto/${selectedCrypto}/ohlc?days=${timeRange}`);
        if (!response.ok) {
          throw new Error('Failed to fetch data');
        }
        const data = await response.json();
        
        const formattedData = data.map(item => ({
          time: item.timestamp / 1000, // Convert from milliseconds to seconds for TV charts
          open: item.open,
          high: item.high,
          low: item.low,
          close: item.close,
        }));

        candlestickSeries.setData(formattedData);
        
        // Fit content
        chart.current.timeScale().fitContent();
      } catch (error) {
        console.error('Error fetching data:', error);
        setError('Failed to load chart data. Please try again later.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();

    // Handle resize
    const handleResize = () => {
      chart.current.applyOptions({
        width: chartContainerRef.current.clientWidth,
      });
    };

    window.addEventListener('resize', handleResize);

    // Cleanup
    return () => {
      window.removeEventListener('resize', handleResize);
      chart.current.remove();
    };
  }, [selectedCrypto, timeRange]);

  return (
    <div className="w-full">
      <div className="border rounded-lg shadow-lg bg-white">
        <div className="p-4 border-b">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-bold text-gray-800">Crypto OHLC Chart</h2>
            <div className="flex gap-4">
              <select
                value={timeRange}
                onChange={(e) => setTimeRange(e.target.value)}
                className="px-4 py-2 border rounded-md bg-white shadow-sm"
              >
                {TIME_RANGES.map(range => (
                  <option key={range.value} value={range.value}>
                    {range.label}
                  </option>
                ))}
              </select>
              <select
                value={selectedCrypto}
                onChange={(e) => setSelectedCrypto(e.target.value)}
                className="px-4 py-2 border rounded-md bg-white shadow-sm"
              >
                {CRYPTO_OPTIONS.map(crypto => (
                  <option key={crypto.id} value={crypto.id}>
                    {crypto.name}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>
        <div className="relative">
          {isLoading && (
            <div className="absolute inset-0 bg-white/75 flex items-center justify-center z-10">
              <div className="text-gray-600">Loading...</div>
            </div>
          )}
          {error && (
            <div className="absolute inset-0 bg-white/75 flex items-center justify-center z-10">
              <div className="text-red-500">{error}</div>
            </div>
          )}
          <div ref={chartContainerRef} className="p-4" />
        </div>
      </div>
    </div>
  );
};

export default CryptoChart;