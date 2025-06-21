import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import CryptoChart from './components/CryptoChart';
import ArbitrageDashboard from './components/arbitrage/ArbitrageDashboard';

const Navigation: React.FC = () => {
  const location = useLocation();
  
  const navItems = [
    { path: '/', label: 'Price Charts', icon: '📊' },
    { path: '/arbitrage', label: 'Arbitrage', icon: '🎯' },
    { path: '/monitoring', label: 'Monitoring', icon: '📈' },
  ];

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex">
            <div className="flex-shrink-0 flex items-center">
              <span className="text-2xl">🏠</span>
              <span className="ml-2 text-xl font-bold text-gray-900">
                Crypto Arbitrage Tracker
              </span>
            </div>
            <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
              {navItems.map((item) => {
                const isActive = location.pathname === item.path;
                
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium ${
                      isActive
                        ? 'border-blue-500 text-gray-900'
                        : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                    }`}
                  >
                    <span className="mr-2">{item.icon}</span>
                    {item.label}
                  </Link>
                );
              })}
            </div>
          </div>
          <div className="flex items-center">
            <button className="p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100">
              ⚙️
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
};

const HomePage: React.FC = () => (
  <div className="space-y-6">
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h1 className="text-3xl font-bold text-gray-900 mb-4">
        Cryptocurrency Price Tracking
      </h1>
      <p className="text-gray-600 mb-6">
        Real-time cryptocurrency price visualization with OHLC data from multiple exchanges.
        Monitor price movements and analyze trading opportunities across different timeframes.
      </p>
    </div>
    <CryptoChart />
  </div>
);

const MonitoringPage: React.FC = () => (
  <div className="space-y-6">
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h1 className="text-3xl font-bold text-gray-900 mb-4">
        System Monitoring
      </h1>
      <p className="text-gray-600 mb-6">
        Monitor the health and performance of the arbitrage detection system.
      </p>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-green-50 p-4 rounded-lg border border-green-200">
          <h3 className="text-lg font-semibold text-green-800 mb-2">Exchange Connections</h3>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-green-700">Binance</span>
              <span className="text-green-600">🟢</span>
            </div>
            <div className="flex justify-between">
              <span className="text-green-700">Coinbase</span>
              <span className="text-green-600">🟢</span>
            </div>
            <div className="flex justify-between">
              <span className="text-green-700">Kraken</span>
              <span className="text-green-600">🟢</span>
            </div>
          </div>
        </div>
        
        <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
          <h3 className="text-lg font-semibold text-blue-800 mb-2">Data Pipeline</h3>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-blue-700">Kafka</span>
              <span className="text-blue-600">🟢</span>
            </div>
            <div className="flex justify-between">
              <span className="text-blue-700">Redis</span>
              <span className="text-blue-600">🟢</span>
            </div>
            <div className="flex justify-between">
              <span className="text-blue-700">TimescaleDB</span>
              <span className="text-blue-600">🟢</span>
            </div>
          </div>
        </div>
        
        <div className="bg-purple-50 p-4 rounded-lg border border-purple-200">
          <h3 className="text-lg font-semibold text-purple-800 mb-2">Performance Metrics</h3>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-purple-700">Latency</span>
              <span className="text-purple-600">45ms</span>
            </div>
            <div className="flex justify-between">
              <span className="text-purple-700">Throughput</span>
              <span className="text-purple-600">2.1k/s</span>
            </div>
            <div className="flex justify-between">
              <span className="text-purple-700">Uptime</span>
              <span className="text-purple-600">99.9%</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
);

const App: React.FC = () => {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Navigation />
        <main className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/arbitrage" element={<ArbitrageDashboard />} />
            <Route path="/monitoring" element={<MonitoringPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
};

export default App;
