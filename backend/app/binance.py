import httpx

from config import logger
from binance_config import BINANCE_API_URL
from models import PriceRequest

class CryptoFetcher:
    def __init__(self):
        self.client = httpx.AsyncClient()
        self.base_url = BINANCE_API_URL
            
    async def get_response(self, request: PriceRequest):
        url = f"{self.base_url}/klines"

        params = {
            "symbol": request.crypto_id,
            "interval": request.interval,
        }
        
        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()  # This will raise an exception for bad status codes
            return response
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error occurred: {str(e)}")
            raise
    