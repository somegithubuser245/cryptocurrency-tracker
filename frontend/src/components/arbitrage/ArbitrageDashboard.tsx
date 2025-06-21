import React, { useState, useEffect, useMemo } from 'react';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  ScatterChart,
  Scatter,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

interface ArbitrageOpportunity {
  symbol: string;
  buy_exchange: string;
  sell_exchange: string;
  buy_price: number;
  sell_price: number;
  gross_profit_pct: number;
  estimated_fees: number;
  net_profit_pct: number;
  liquidity_score: number;
  confidence_score: number;
  timestamp: string;
  estimated_volume?: number;
  execution_time_estimate?: number;
}

interface ArbitrageResponse {
  opportunities: ArbitrageOpportunity[];
}

const ArbitrageDashboard: React.FC = () => {
  const [opportunities, setOpportunities] = useState<ArbitrageOpportunity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState({
    minProfit: 0.5,
    minConfidence: 0.5,
    symbol: 'all'
  });

  useEffect(() => {
    const fetchOpportunities = async () => {
      try {
        const response = await fetch('http://localhost:8002/opportunities');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data: ArbitrageResponse = await response.json();
        setOpportunities(data.opportunities || []);
        setError(null);
      } catch (err) {
        console.error('Error fetching opportunities:', err);
        setError('Failed to fetch arbitrage opportunities');
      } finally {
        setLoading(false);
      }
    };

    // Initial fetch
    fetchOpportunities();

    // Set up real-time updates every 5 seconds
    const interval = setInterval(fetchOpportunities, 5000);
    return () => clearInterval(interval);
  }, []);

  const filteredOpportunities = opportunities.filter(opp => {
    const meetsMinProfit = (opp.net_profit_pct * 100) >= filter.minProfit;
    const meetsMinConfidence = opp.confidence_score >= filter.minConfidence;
    const meetsSymbolFilter = filter.symbol === 'all' || opp.symbol === filter.symbol;
    
    return meetsMinProfit && meetsMinConfidence && meetsSymbolFilter;
  });

  // Chart data preparation
  const chartData = useMemo(() => {
    // Profit distribution by symbol
    const profitBySymbol = opportunities.reduce((acc, opp) => {
      const symbol = opp.symbol.split('/')[0]; // Get base currency
      if (!acc[symbol]) {
        acc[symbol] = { symbol, avgProfit: 0, count: 0, totalProfit: 0, maxProfit: 0, totalVolume: 0 };
      }
      acc[symbol].totalProfit += opp.net_profit_pct * 100;
      acc[symbol].count += 1;
      acc[symbol].avgProfit = acc[symbol].totalProfit / acc[symbol].count;
      acc[symbol].maxProfit = Math.max(acc[symbol].maxProfit, opp.net_profit_pct * 100);
      acc[symbol].totalVolume += opp.estimated_volume || 0;
      return acc;
    }, {} as Record<string, any>);

    // Exchange pair analysis
    const exchangePairs = opportunities.reduce((acc, opp) => {
      const pairKey = `${opp.buy_exchange}→${opp.sell_exchange}`;
      if (!acc[pairKey]) {
        acc[pairKey] = { 
          pair: pairKey, 
          buyExchange: opp.buy_exchange,
          sellExchange: opp.sell_exchange,
          count: 0, 
          avgProfit: 0, 
          totalProfit: 0,
          avgConfidence: 0,
          totalConfidence: 0
        };
      }
      acc[pairKey].count += 1;
      acc[pairKey].totalProfit += opp.net_profit_pct * 100;
      acc[pairKey].avgProfit = acc[pairKey].totalProfit / acc[pairKey].count;
      acc[pairKey].totalConfidence += opp.confidence_score * 100;
      acc[pairKey].avgConfidence = acc[pairKey].totalConfidence / acc[pairKey].count;
      return acc;
    }, {} as Record<string, any>);

    // Profit vs Confidence scatter data
    const scatterData = opportunities.map((opp, index) => ({
      confidence: opp.confidence_score * 100,
      profit: opp.net_profit_pct * 100,
      symbol: opp.symbol.split('/')[0],
      volume: opp.estimated_volume || 0,
      id: index
    }));

    // Historical trend simulation (mock data)
    const timeData = Array.from({ length: 24 }, (_, i) => ({
      hour: `${i.toString().padStart(2, '0')}:00`,
      opportunities: Math.floor(Math.random() * 15) + opportunities.length * 0.8,
      avgProfit: parseFloat((Math.random() * 1.5 + 0.8).toFixed(2)),
      volume: Math.floor(Math.random() * 800000) + 200000,
      successRate: Math.floor(Math.random() * 30) + 70
    }));

    // Exchange popularity
    const exchangeData = opportunities.reduce((acc, opp) => {
      // Count buy exchange appearances
      if (!acc[opp.buy_exchange]) {
        acc[opp.buy_exchange] = { exchange: opp.buy_exchange, buyCount: 0, sellCount: 0, totalCount: 0 };
      }
      acc[opp.buy_exchange].buyCount += 1;
      acc[opp.buy_exchange].totalCount += 1;

      // Count sell exchange appearances
      if (!acc[opp.sell_exchange]) {
        acc[opp.sell_exchange] = { exchange: opp.sell_exchange, buyCount: 0, sellCount: 0, totalCount: 0 };
      }
      acc[opp.sell_exchange].sellCount += 1;
      acc[opp.sell_exchange].totalCount += 1;

      return acc;
    }, {} as Record<string, any>);

    return {
      symbolData: Object.values(profitBySymbol).sort((a: any, b: any) => b.avgProfit - a.avgProfit),
      pairData: Object.values(exchangePairs).sort((a: any, b: any) => b.avgProfit - a.avgProfit).slice(0, 8),
      scatterData,
      timeData,
      exchangeData: Object.values(exchangeData).sort((a: any, b: any) => b.totalCount - a.totalCount)
    };
  }, [opportunities]);

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D', '#FFC658', '#FF7C7C'];

  const getProfitColor = (profit: number) => {
    if (profit >= 2) return 'bg-green-100 text-green-800';
    if (profit >= 1) return 'bg-green-50 text-green-700';
    if (profit >= 0.5) return 'bg-yellow-50 text-yellow-700';
    return 'bg-red-50 text-red-700';
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-green-600';
    if (confidence >= 0.6) return 'text-yellow-600';
    return 'text-red-500';
  };

  const formatTime = (timestamp: string) => {
    const time = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - time.getTime();
    const diffSecs = Math.floor(diffMs / 1000);
    
    if (diffSecs < 60) return `${diffSecs}s ago`;
    if (diffSecs < 3600) return `${Math.floor(diffSecs / 60)}m ago`;
    return `${Math.floor(diffSecs / 3600)}h ago`;
  };

  const formatExecutionTime = (seconds?: number) => {
    if (!seconds) return 'N/A';
    if (seconds < 60) return `${seconds}s`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${seconds % 60}s`;
    return `${Math.floor(seconds / 3600)}h ${Math.floor((seconds % 3600) / 60)}m`;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-md p-4">
        <div className="flex items-center">
          <span className="text-red-800">⚠️ {error}</span>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with Stats */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Arbitrage Opportunities Dashboard</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-blue-50 p-4 rounded-lg">
            <div className="flex items-center">
              <span className="text-sm font-medium text-blue-600">📊 Total Opportunities</span>
            </div>
            <p className="text-2xl font-bold text-blue-900">{opportunities.length}</p>
          </div>
          
          <div className="bg-green-50 p-4 rounded-lg">
            <div className="flex items-center">
              <span className="text-sm font-medium text-green-600">📈 High Profit (&gt;1%)</span>
            </div>
            <p className="text-2xl font-bold text-green-900">
              {opportunities.filter(opp => opp.net_profit_pct > 0.01).length}
            </p>
          </div>
          
          <div className="bg-yellow-50 p-4 rounded-lg">
            <div className="flex items-center">
              <span className="text-sm font-medium text-yellow-600">⏱️ Quick Execution (&lt;5m)</span>
            </div>
            <p className="text-2xl font-bold text-yellow-900">
              {opportunities.filter(opp => (opp.execution_time_estimate || 0) < 300).length}
            </p>
          </div>
          
          <div className="bg-purple-50 p-4 rounded-lg">
            <div className="flex items-center">
              <span className="text-sm font-medium text-purple-600">🎯 High Confidence (&gt;80%)</span>
            </div>
            <p className="text-2xl font-bold text-purple-900">
              {opportunities.filter(opp => opp.confidence_score > 0.8).length}
            </p>
          </div>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap gap-4 mb-6">
          <div className="flex items-center space-x-2">
            <label className="text-sm font-medium text-gray-700">Min Profit %:</label>
            <select
              value={filter.minProfit}
              onChange={(e) => setFilter(prev => ({ ...prev, minProfit: Number(e.target.value) }))}
              className="border border-gray-300 rounded-md px-3 py-1 text-sm"
            >
              <option value={0}>Any</option>
              <option value={0.5}>0.5%</option>
              <option value={1}>1%</option>
              <option value={2}>2%</option>
            </select>
          </div>
          
          <div className="flex items-center space-x-2">
            <label className="text-sm font-medium text-gray-700">Min Confidence:</label>
            <select
              value={filter.minConfidence}
              onChange={(e) => setFilter(prev => ({ ...prev, minConfidence: Number(e.target.value) }))}
              className="border border-gray-300 rounded-md px-3 py-1 text-sm"
            >
              <option value={0}>Any</option>
              <option value={0.5}>50%</option>
              <option value={0.7}>70%</option>
              <option value={0.8}>80%</option>
            </select>
          </div>
          
          <div className="flex items-center space-x-2">
            <label className="text-sm font-medium text-gray-700">Symbol:</label>
            <select
              value={filter.symbol}
              onChange={(e) => setFilter(prev => ({ ...prev, symbol: e.target.value }))}
              className="border border-gray-300 rounded-md px-3 py-1 text-sm"
            >
              <option value="all">All</option>
              {Array.from(new Set(opportunities.map(opp => opp.symbol))).map(symbol => (
                <option key={symbol} value={symbol}>{symbol}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Profit by Symbol Chart */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Profit by Cryptocurrency</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData.symbolData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="symbol" />
              <YAxis />
              <Tooltip 
                formatter={(value: any, name: string) => [
                  `${parseFloat(value).toFixed(2)}%`, 
                  name === 'avgProfit' ? 'Avg Profit' : name === 'maxProfit' ? 'Max Profit' : 'Count'
                ]}
              />
              <Legend />
              <Bar dataKey="avgProfit" fill="#8884d8" name="Avg Profit %" />
              <Bar dataKey="maxProfit" fill="#82ca9d" name="Max Profit %" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Exchange Pairs Performance */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Top Exchange Pairs</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData.pairData} layout="horizontal">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" />
              <YAxis dataKey="pair" type="category" width={120} />
              <Tooltip formatter={(value: any) => [`${parseFloat(value).toFixed(2)}%`, 'Avg Profit']} />
              <Bar dataKey="avgProfit" fill="#ffc658" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Profit vs Confidence Scatter Plot */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Profit vs Confidence Analysis</h3>
          <ResponsiveContainer width="100%" height={300}>
            <ScatterChart data={chartData.scatterData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="confidence" name="Confidence" unit="%" />
              <YAxis dataKey="profit" name="Profit" unit="%" />
              <Tooltip 
                cursor={{ strokeDasharray: '3 3' }}
                formatter={(value: any, name: string) => [
                  `${parseFloat(value).toFixed(2)}%`, 
                  name === 'confidence' ? 'Confidence' : 'Profit'
                ]}
              />
              <Scatter dataKey="profit" fill="#8884d8" />
            </ScatterChart>
          </ResponsiveContainer>
        </div>

        {/* 24h Trend Analysis */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">24h Opportunity Trends</h3>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={chartData.timeData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="hour" />
              <YAxis />
              <Tooltip />
              <Area type="monotone" dataKey="opportunities" stroke="#8884d8" fill="#8884d8" fillOpacity={0.3} />
              <Area type="monotone" dataKey="avgProfit" stroke="#82ca9d" fill="#82ca9d" fillOpacity={0.3} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Exchange Activity Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Exchange Activity Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={chartData.exchangeData.slice(0, 8)}
                cx="50%"
                cy="50%"
                outerRadius={80}
                fill="#8884d8"
                dataKey="totalCount"
                label={({ exchange, totalCount }) => `${exchange}: ${totalCount}`}
              >
                {chartData.exchangeData.slice(0, 8).map((entry: any, index: number) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Volume & Success Rate Trend</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData.timeData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="hour" />
              <YAxis yAxisId="left" />
              <YAxis yAxisId="right" orientation="right" />
              <Tooltip />
              <Legend />
              <Line yAxisId="left" type="monotone" dataKey="volume" stroke="#8884d8" name="Volume" />
              <Line yAxisId="right" type="monotone" dataKey="successRate" stroke="#82ca9d" name="Success Rate %" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Opportunities Table */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Current Opportunities</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Symbol & Route
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Prices
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Profit
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Scores
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Execution
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Age
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredOpportunities.map((opp, index) => (
                <tr key={index} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{opp.symbol}</div>
                    <div className="text-sm text-gray-500">
                      {opp.buy_exchange} → {opp.sell_exchange}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">
                      Buy: ${opp.buy_price.toFixed(4)}
                    </div>
                    <div className="text-sm text-gray-500">
                      Sell: ${opp.sell_price.toFixed(4)}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getProfitColor(opp.net_profit_pct * 100)}`}>
                      {(opp.net_profit_pct * 100).toFixed(2)}%
                    </div>
                    <div className="text-xs text-gray-500 mt-1">
                      Fees: {(opp.estimated_fees * 100).toFixed(2)}%
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center space-x-2">
                      <div className="text-sm">
                        <span className={`font-medium ${getConfidenceColor(opp.confidence_score)}`}>
                          {(opp.confidence_score * 100).toFixed(0)}%
                        </span>
                        <span className="text-gray-500 ml-1">conf</span>
                      </div>
                    </div>
                    <div className="text-xs text-gray-500">
                      Liquidity: {(opp.liquidity_score * 100).toFixed(0)}%
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">
                      {formatExecutionTime(opp.execution_time_estimate)}
                    </div>
                    {opp.estimated_volume && (
                      <div className="text-xs text-gray-500">
                        Vol: {opp.estimated_volume.toFixed(4)}
                      </div>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {formatTime(opp.timestamp)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        {filteredOpportunities.length === 0 && (
          <div className="text-center py-12">
            <div className="mx-auto h-12 w-12 text-gray-400 text-4xl">📉</div>
            <h3 className="mt-2 text-sm font-medium text-gray-900">No opportunities found</h3>
            <p className="mt-1 text-sm text-gray-500">
              Try adjusting your filters or wait for new opportunities to be detected.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ArbitrageDashboard;