import { useEffect, useState } from "react";
import ChartCard from "./components/ChartCard";

function App() {
  const [configData, setConfigData] = useState(Array<{id: string, name: string}>);
  const [timeRangesData, setTimeRanges] = useState(Array<{id: string, name: string}>) 
  useEffect(() => {
    let ignore = false;

    async function fetchCryptoData() {
      let response = await fetch('http://127.0.0.1:8000/api/crypto/config/pairs')
      let data = await response.json()
      let processedPairsData : Array<{id: string, name: string}> = []
      Object.entries(data).forEach((entry) => {
        processedPairsData.push({id: entry[0], name: entry[1] as string})
      })

      response = await fetch('http://127.0.0.1:8000/api/crypto/config/timeranges')
      data = await response.json()
      let processedRangesData : Array<{id: string, name: string}> = []
      Object.entries(data).forEach((entry) => {
        processedRangesData.push({id: entry[0], name: entry[1] as string})
      })

      if (!ignore) {
        setConfigData(processedPairsData)
        setTimeRanges(processedRangesData)
      }
    }

    fetchCryptoData();

    return () => {
      ignore = true;
    }
  }, [])

  return configData.length > 0 && <ChartCard cryptoPairs={configData} timeRanges={timeRangesData}/>;
}

export default App;
