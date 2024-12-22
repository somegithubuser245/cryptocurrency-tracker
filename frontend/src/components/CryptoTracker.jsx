import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

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

  const fetchPriceData = async (cryptoId) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`http://localhost:8000/api/crypto/${cryptoId}/history`);
      const data = await response.json();
      setPriceData(data.data);
    } catch (error) {
      console.error('Error fetching price data:', error);
      setError('Failed to load price data');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchPriceData(selectedCrypto);
  }, [selectedCrypto]);

  // Find the currently selected crypto name
  const selectedCryptoName = cryptoOptions.find(crypto => crypto.id === selectedCrypto)?.name;

  return (
    <div className="w-full h-screen p-4">
        <div className="h-full bg-white rounded-lg shadow-lg">
        <div className="bg-white rounded-lg shadow-lg">
          {/* Header */}
          <div className="p-6 border-b">
            <div className="flex justify-between items-center">
              <div>
                <h2 className="text-2xl font-bold text-gray-800">Crypto Price Tracker</h2>
                <p className="text-gray-600 mt-1">Tracking {selectedCryptoName}</p>
              </div>
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
          <div className="p-6">
            {error && (
              <div className="text-red-500 text-center py-4">
                {error}
              </div>
            )}
            
            {isLoading ? (
              <div className="h-96 flex items-center justify-center">
                <div className="text-gray-600">Loading...</div>
              </div>
            ) : (
              <div className="h-96">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={priceData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis
                      dataKey="datetime"
                      tickFormatter={(value) => {
                        const date = new Date(value);
                        return `${date.toLocaleDateString()} ${date.toLocaleTimeString()}`;
                      }}
                    />
                    <YAxis />
                    <Tooltip
                      labelFormatter={(value) => new Date(value).toLocaleString()}
                      formatter={(value) => [`$${value.toFixed(2)}`, selectedCryptoName]}
                    />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="price"
                      stroke="#2563eb"
                      name={selectedCryptoName}
                      dot={false}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            )}
            
            {!isLoading && !error && priceData.length > 0 && (
              <div className="mt-6 p-4 bg-gray-50 rounded-lg">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-gray-600">Current Price</p>
                    <p className="text-2xl font-bold text-gray-800">
                      ${priceData[priceData.length - 1].price.toFixed(2)}
                    </p>
                  </div>
                  <div>
                    <p className="text-gray-600">Last Updated</p>
                    <p className="text-2xl font-bold text-gray-800">
                      {new Date(priceData[priceData.length - 1].datetime).toLocaleString()}
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CryptoTracker;