import React, { useEffect, useRef, useState } from 'react';
import { createChart, IChartApi, Time, } from 'lightweight-charts';

// Type definitions
interface OHLCData {
  time: Time;
  open: number;
  high: number;
  low: number;
  close: number;
}

interface ConfigData {
  [key: string]: string;
}

const CryptoChart: React.FC = () => {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chart = useRef<IChartApi | null>(null);
  const [selectedPair, setSelectedPair] = useState<string>('BTCUSDT');
  const [timeRange, setTimeRange] = useState<string>('4h');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [supportedPairs, setSupportedPairs] = useState<ConfigData>({});
  const [timeRanges, setTimeRanges] = useState<ConfigData>({});

  // Fetch configuration data
  useEffect(() => {
    const fetchConfigs = async () => {
      try {
        const [pairsResponse, timeResponse] = await Promise.all([
          fetch('http://localhost:8000/api/crypto/config/pairs'),
          fetch('http://localhost:8000/api/crypto/config/timeranges')
        ]);

        if (!pairsResponse.ok || !timeResponse.ok) {
          throw new Error('Failed to fetch configuration data');
        }

        const pairs = await pairsResponse.json();
        const times = await timeResponse.json();

        setSupportedPairs(pairs);
        setTimeRanges(times);
      } catch (err) {
        console.error('Error fetching configuration:', err);
        setError('Failed to load configuration. Please try again later.');
      }
    };

    fetchConfigs();
  }, []);

  useEffect(() => {
    if (!chartContainerRef.current) return;

    chart.current = createChart(chartContainerRef.current, {
      layout: {
        background: { color: '#222' },
        textColor: '#DDD',
      },
      width: chartContainerRef.current.clientWidth,
      height: 500,
      timeScale: {
        timeVisible: true,
        secondsVisible: false,
      },
      grid: {
        vertLines: { color: '#444' },
        horzLines: { color: '#444' },
      },
      crosshair: {
        mode: 0,
        vertLine: {
          color: '#C3BCDB44',
          labelBackgroundColor: '#9B7DFF',
        },
        horzLine: {
          color: '#9B7DFF',
          labelBackgroundColor: '#9B7DFF',
        },
      },
    });

    chart.current.timeScale().applyOptions({
      borderColor: '#71649C'
    });

    const candlestickSeries = chart.current.addCandlestickSeries({
      wickUpColor: 'rgb(54, 116, 217)',
      upColor: 'rgb(54, 116, 217)',
      wickDownColor: 'rgb(225, 50, 85)',
      downColor: 'rgb(225, 50, 85)',
      borderVisible: false,
    });

    const fetchData = async (): Promise<void> => {
    setIsLoading(true);
    setError(null);
    try {
        const response = await fetch(
            `http://localhost:8000/api/crypto/${selectedPair}/ohlc?interval=${timeRange}`
        );
        if (!response.ok) {
            throw new Error('Failed to fetch data');
        }
        const data: OHLCData[] = await response.json();
        
        // No need for data transformation, use directly
        candlestickSeries.setData(data);
        chart.current?.timeScale().fitContent();
    } catch (err) {
        console.error('Error fetching data:', err);
        setError('Failed to load chart data. Please try again later.');
    } finally {
        setIsLoading(false);
    }
};

    fetchData();

    const handleResize = (): void => {
      if (chart.current && chartContainerRef.current) {
        chart.current.applyOptions({
          width: chartContainerRef.current.clientWidth,
        });
      }
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      if (chart.current) {
        chart.current.remove();
      }
    };
  }, [selectedPair, timeRange]);

  const handlePairChange = (e: React.ChangeEvent<HTMLSelectElement>): void => {
    setSelectedPair(e.target.value);
  };

  const handleTimeRangeChange = (e: React.ChangeEvent<HTMLSelectElement>): void => {
    setTimeRange(e.target.value);
  };

  return (
    <div className="w-full bg-black rounded-xl p-3">
      <div className="flex flex-row justify-end pb-2">
        <div className="basis-1/2 justify-self-start self-center">
          <h2 className='text-white text-left text-xl mx-3'>
            {supportedPairs[selectedPair] || selectedPair} OHLC Chart
          </h2>
        </div>
        <div className='flex flex-row basis-1/2 justify-end'>
          <select
            value={timeRange}
            onChange={handleTimeRangeChange}
            className="m-2 p-2 rounded-xl border-2 border-transparent"
          >
            {Object.entries(timeRanges).map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
          <select
            value={selectedPair}
            onChange={handlePairChange}
            className="m-2 p-2 rounded-xl border-2"
          >
            {Object.entries(supportedPairs).map(([pair, name]) => (
              <option key={pair} value={pair}>
                {name}
              </option>
            ))}
          </select>
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
        <div ref={chartContainerRef} className="p-1" />
      </div>
    </div>
  );
};

export default CryptoChart;