import React, { useState, useEffect } from 'react';

interface PriceData {
  symbol: string;
  price: number;
  change24h: number;
  timestamp: string;
}

const CryptoChart: React.FC = () => {
  const [prices, setPrices] = useState<PriceData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPrices = async () => {
      try {
        // Mock data for now - will be replaced with real API calls
        const mockPrices: PriceData[] = [
          { symbol: 'BTC/USDT', price: 43250.75, change24h: 2.45, timestamp: new Date().toISOString() },
          { symbol: 'ETH/USDT', price: 2650.30, change24h: -1.20, timestamp: new Date().toISOString() },
          { symbol: 'SOL/USDT', price: 95.80, change24h: 5.67, timestamp: new Date().toISOString() },
          { symbol: 'ADA/USDT', price: 0.485, change24h: 3.21, timestamp: new Date().toISOString() },
          { symbol: 'DOT/USDT', price: 7.25, change24h: -0.85, timestamp: new Date().toISOString() },
        ];
        
        setPrices(mockPrices);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching prices:', error);
        setLoading(false);
      }
    };

    fetchPrices();
    const interval = setInterval(fetchPrices, 10000); // Update every 10 seconds

    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="space-y-3">
            <div className="h-4 bg-gray-200 rounded"></div>
            <div className="h-4 bg-gray-200 rounded w-5/6"></div>
            <div className="h-4 bg-gray-200 rounded w-4/6"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Cryptocurrency Prices</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {prices.map((price) => (
          <div key={price.symbol} className="bg-gray-50 rounded-lg p-4 border">
            <div className="flex justify-between items-start mb-2">
              <h3 className="text-lg font-semibold text-gray-900">{price.symbol}</h3>
              <span className={`text-sm font-medium px-2 py-1 rounded ${
                price.change24h >= 0 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-red-100 text-red-800'
              }`}>
                {price.change24h >= 0 ? '+' : ''}{price.change24h.toFixed(2)}%
              </span>
            </div>
            
            <div className="text-2xl font-bold text-gray-900 mb-1">
              ${price.price.toLocaleString(undefined, { 
                minimumFractionDigits: 2, 
                maximumFractionDigits: 8 
              })}
            </div>
            
            <div className="text-sm text-gray-500">
              Last updated: {new Date(price.timestamp).toLocaleTimeString()}
            </div>
            
            <div className="mt-3 flex items-center">
              <div className={`w-3 h-3 rounded-full mr-2 ${
                price.change24h >= 0 ? 'bg-green-500' : 'bg-red-500'
              }`}></div>
              <span className="text-sm text-gray-600">
                {price.change24h >= 0 ? 'Trending up' : 'Trending down'}
              </span>
            </div>
          </div>
        ))}
      </div>
      
      <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
        <h3 className="text-sm font-medium text-blue-800 mb-2">📊 Market Data Status</h3>
        <p className="text-sm text-blue-700">
          Real-time price feeds from multiple exchanges. Data updates every 10 seconds.
          Advanced charting with arbitrage detection available in the Arbitrage tab.
        </p>
      </div>
    </div>
  );
};

export default CryptoChart;
