import { useEffect, useState } from "react";
import Chart from "./components/Chart";

function App() {
  const [cryptoData, setCryptoData] = useState([]);

  useEffect(() => {
    let ignore = false;

    async function fetchCryptoData() {
      const response = await fetch('http://127.0.0.1:8000/api/crypto/BTCUSDT/klines')
      const data = await response.json()
      if (!ignore) {
        setCryptoData(data)
      }
    }

    fetchCryptoData()

    return () => {
      ignore = true;
    }
  }, [])

  return <Chart data={cryptoData} ></Chart>;
}

export default App;
