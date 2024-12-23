import React, { useEffect, useRef, useState } from 'react';
import { createChart, IChartApi, Time, ISeriesApi, CandlestickData } from 'lightweight-charts';

// Type definitions
interface CryptoOption {
  id: string;
  name: string;
}

interface TimeRange {
  value: string;
  label: string;
}

interface OHLCData {
  timestamp: number;
  open: number;
  high: number;
  low: number;
  close: number;
}

const CRYPTO_OPTIONS: CryptoOption[] = [
  { id: 'bitcoin', name: 'Bitcoin' },
  { id: 'ethereum', name: 'Ethereum' },
  { id: 'solana', name: 'Solana' },
  { id: 'dogecoin', name: 'Dogecoin' },
  { id: 'cardano', name: 'Cardano' }
];

const TIME_RANGES: TimeRange[] = [
  { value: '1', label: '24 Hours' },
  { value: '7', label: '7 Days' },
  { value: '30', label: '30 Days' },
  { value: '90', label: '90 Days' }
];

const CryptoChart: React.FC = () => {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chart = useRef<IChartApi | null>(null);
  const [selectedCrypto, setSelectedCrypto] = useState<string>('bitcoin');
  const [timeRange, setTimeRange] = useState<string>('7');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!chartContainerRef.current) return;

    // Create chart instance
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
        // Change mode from default 'magnet' to 'normal'.
        // Allows the crosshair to move freely without snapping to datapoints
        mode: 0,

        // Vertical crosshair line (showing Date in Label)
        vertLine: {
            color: '#C3BCDB44',
            labelBackgroundColor: '#9B7DFF',
        },

        // Horizontal crosshair line (showing Price in Label)
        horzLine: {
            color: '#9B7DFF',
            labelBackgroundColor: '#9B7DFF',
        },
    },
    });

    chart.current.timeScale().applyOptions({
        borderColor: '#71649C'
    })

    // Create candlestick series
    const candlestickSeries = chart.current.addCandlestickSeries({
        wickUpColor: 'rgb(54, 116, 217)',
        upColor: 'rgb(54, 116, 217)',
        wickDownColor: 'rgb(225, 50, 85)',
        downColor: 'rgb(225, 50, 85)',
        borderVisible: false,
    });

    // Add data
    const fetchData = async (): Promise<void> => {
      setIsLoading(true);
      setError(null);
      try {
        const response = await fetch(`http://localhost:8000/api/crypto/${selectedCrypto}/ohlc?days=${timeRange}`);
        if (!response.ok) {
          throw new Error('Failed to fetch data');
        }
        const data: OHLCData[] = await response.json();
        
        const formattedData: CandlestickData<Time>[] = data.map(item => ({
          time: (item.timestamp / 1000) as Time,
          open: item.open,
          high: item.high,
          low: item.low,
          close: item.close,
        }));

        candlestickSeries.setData(formattedData);
        
        // Fit content
        chart.current?.timeScale().fitContent();
      } catch (err) {
        console.error('Error fetching data:', err);
        setError('Failed to load chart data. Please try again later.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();

    // Handle resize
    const handleResize = (): void => {
      if (chart.current && chartContainerRef.current) {
        chart.current.applyOptions({
          width: chartContainerRef.current.clientWidth,
        });
      }
    };

    window.addEventListener('resize', handleResize);

    // Cleanup
    return () => {
      window.removeEventListener('resize', handleResize);
      if (chart.current) {
        chart.current.remove();
      }
    };
  }, [selectedCrypto, timeRange]);

  const handleCryptoChange = (e: React.ChangeEvent<HTMLSelectElement>): void => {
    setSelectedCrypto(e.target.value);
  };

  const handleTimeRangeChange = (e: React.ChangeEvent<HTMLSelectElement>): void => {
    setTimeRange(e.target.value);
  };

  return (
    <div className="w-full bg-black rounded-xl p-3">
            <div className="flex flex-row justify-end pb-2">
            <div className="basis-1/2 justify-self-start self-center">
                <h2 className='text-white text-left text-xl mx-3'>{selectedCrypto.toUpperCase()} OHLC Chart</h2>
            </div>
              <div className='flex flex-row basis-1/2 justify-end'>
                <select
                    value={timeRange}
                    onChange={handleTimeRangeChange}
                    className="m-2 p-2 rounded-xl border-2 border-trasparent"
                >
                    {TIME_RANGES.map(range => (
                    <option key={range.value} value={range.value}>
                        {range.label}
                    </option>
                    ))}
                </select>
                <select
                    value={selectedCrypto}
                    onChange={handleCryptoChange}
                    className="m-2 p-2 rounded-xl border-2"
                >
                    {CRYPTO_OPTIONS.map(crypto => (
                    <option key={crypto.id} value={crypto.id}>
                        {crypto.name}
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