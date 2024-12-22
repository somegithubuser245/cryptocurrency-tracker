import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import axios from 'axios';

const CryptoTracker = () => {
  const [selectedCrypto, setSelectedCrypto] = useState('bitcoin');
  const [priceData, setPriceData] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const cryptoOptions = [
    { id: 'bitcoin', name: 'Bitcoin' },
    { id: 'ethereum', name: 'Ethereum' },
    { id: 'dogecoin', name: 'Dogecoin' },
    { id: 'cardano', name: 'Cardano' },
    { id: 'solana', name: 'Solana' }
  ];

  // Fetch price data for selected crypto
  const fetchPriceData = async (cryptoId) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await axios.get(`http://localhost:8000/api/crypto/${cryptoId}/history`);
      setPriceData(response.data.data);
    } catch (error) {
      console.error('Error fetching price data:', error);
      setError('Failed to load price data');
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch data when selected crypto changes
  useEffect(() => {
    fetchPriceData(selectedCrypto);
  }, [selectedCrypto]);

  return (
    <div className="p-4 w-full h-screen">
      <div className="bg-white rounded-lg shadow-lg">
        {/* Header */}
        <div className="p-4 border-b">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-bold text-gray-800">Crypto Price Tracker</h2>
            <select
              value={selectedCrypto}
              onChange={(e) => setSelectedCrypto(e.target.value)}
              className="px-4 py-2 border rounded-md bg-white shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={isLoading}
            >
              {cryptoOptions.map(crypto => (
                <option key={crypto.id} value={crypto.id}>
                  {crypto.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Content */}
        <div className="p-4 w-full h-screen">
          {error && (
            <div className="text-red-500 text-center py-4">
              {error}
            </div>
          )}
          
          {isLoading ? (
            <div className="h-64 flex items-center justify-center">
              <div className="text-gray-600">Loading...</div>
            </div>
          ) : (
            <div className="h-[calc(100vh-200px)]">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={priceData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="datetime" 
                    tickFormatter={(value) => new Date(value).toLocaleDateString()}
                  />
                  <YAxis />
                  <Tooltip 
                    labelFormatter={(value) => new Date(value).toLocaleString()}
                    formatter={(value) => [`$${value.toFixed(2)}`, "Price"]}
                  />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="price"
                    stroke="#2563eb"
                    name="Price (USD)"
                    dot={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}
          
          {!isLoading && !error && priceData.length > 0 && (
            <div className="mt-4 text-center">
              <p className="text-lg font-semibold text-gray-800">
                Current Price: ${priceData[priceData.length - 1].price.toFixed(2)}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CryptoTracker;