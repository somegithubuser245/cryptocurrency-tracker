import httpx

from app.config.binance_config import binance_settings
from app.config.config import logger
from app.models.schemas import PriceRequest


class CryptoFetcher:
    """This is basically a reqest wrapper
    It just adds some binance API related PATHs
    and makes some additional checks
    """
    def __init__(self) -> None:
        self.client = httpx.AsyncClient()
        self.base_url = binance_settings.BINANCE_API_URL

    async def get_response(self, request: PriceRequest) -> str:
        url = f"{self.base_url}/{request.data_type}"

        params = {
            "symbol": request.crypto_id,
            "interval": request.interval,
        }
        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()  # This will raise an exception for bad status codes
            return response.text
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error occurred: {str(e)}")
            raise
