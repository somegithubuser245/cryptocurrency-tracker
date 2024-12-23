import CryptoChart from './components/CryptoChart'

function App() {
  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">
          Crypto Price Tracker
        </h1>
        <CryptoChart />
      </div>
    </div>
  )
}

export default App