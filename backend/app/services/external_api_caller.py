import httpx
import json
from okx import MarketData

from app.config import binance_config, okx_config
from app.config.config import logger, ApiProvider
from app.models.schemas import KlinesRequest


class CryptoFetcher:
    """This is basically a reqest wrapper
    It just adds some binance API related PATHs
    and makes some additional checks
    """
    def __init__(self) -> None:
        self.client = httpx.AsyncClient()

    async def get_response(self, request: KlinesRequest) -> str:
        match request.api_provider:
            case ApiProvider.BINANCE:
                return await self._get_from_binance(request)
            case ApiProvider.OKX:
                return await self._get_from_okx(request)

    async def _get_from_binance(self, request: KlinesRequest) -> str:
        url = f"{binance_config.BINANCE_API_URL}/klines"

        params = {
            "symbol": binance_config.SUPPORTED_PAIRS[request.crypto_id],
            "interval": binance_config.TIME_RANGES[request.interval],
        }

        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()  # This will raise an exception for bad status codes
            # logger.info(f"BINANCE ALSO HIT, BLYEAT: {response.text}")
            return response.text
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error occurred: {str(e)}")
            raise

    async def _get_from_okx(self, request: KlinesRequest) -> str:
        market_data_api = MarketData.MarketAPI()
        market_data = json.dumps(market_data_api.get_candlesticks(
            instId=okx_config.SUPPORTED_PAIRS[request.crypto_id],
            bar=okx_config.TIME_RANGES[request.interval]
            )["data"])
        return market_data