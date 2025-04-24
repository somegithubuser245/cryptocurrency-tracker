import json
import logging

from app.config import config
from app.models.schemas import OHLCData, KlinesRequest

from .external_api_caller import CryptoFetcher
from .caching import Cacher

from app.config.config import logger


class ApiCallManager:
    """Main class that handles calls from FastAPI"""

    def __init__(self) -> None:
        self.data_fetcher = CryptoFetcher()
        self.redis_cacher = Cacher()

    async def get_price_stats(self, request: KlinesRequest) -> dict:
        # look if request is already cached and return it if so
        raw_data = self.redis_cacher.get(request)
        if raw_data: return self._format_data(raw_data, request)

        # if not, make request to binance api
        raw_data = await self.data_fetcher.get_response(request)
        # cache response
        ttl = config.CACHE_TTL_CONFIG[request.interval]
        self.redis_cacher.set(raw_data, request, ttl)

        # return to API caller in readable format
        return self._format_data(raw_data, request)

    def get_config_data(self, config_type: str) -> dict:
        match config_type:
            case "timeranges":
                return config.TIME_RANGES
            case "pairs":
                return config.SUPPORTED_PAIRS

        raise ValueError(f"Unsupported config type: {config_type}")

    # Helper functions for API caller to have better format
    def _format_data(self, data: str, request: KlinesRequest) -> dict:
        # slalable for other data types. current implementation only has
        # klines. If you plan to add other binance data, you need to
        # add another format method
        json_data = json.loads(data)

        if request.api_provider == 'okx':
            json_data.sort(key=lambda x: float(x[0]))
        return [OHLCData.from_external_api(request.api_provider, price_entry) 
                for price_entry in json_data]
