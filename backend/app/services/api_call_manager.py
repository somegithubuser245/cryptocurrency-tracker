import json

from app.config.binance_config import binance_settings
from app.models.schemas import OHLCData, PriceRequest

from .binance import CryptoFetcher
from .caching import Cacher


class ApiCallManager:
    """Main class that handles calls from FastAPI"""

    def __init__(self) -> None:
        self.data_fetcher = CryptoFetcher()
        self.redis_cacher = Cacher()

    async def get_price_stats(self, request: PriceRequest) -> dict:
        self._validate_request(request)

        # look if request is already cached and return it if so
        # raw_data = self.redis_cacher.get(request)
        # if raw_data is not None:
        #     return self.format_data(raw_data, request.data_type)

        # if not, make request to binance api
        response = await self.data_fetcher.get_response(request)

        # cache response
        # ttl = binance_settings.CACHE_TTL_CONFIG[request.interval]
        # self.redis_cacher.set(raw_data, request, ttl)

        # return to API caller in readable format
        return self._format_data(response, request.data_type)

    def get_config_data(self, config_type: str) -> dict:
        match config_type:
            case "timeranges":
                return binance_settings.TIME_RANGES
            case "pairs":
                return binance_settings.SUPPORTED_PAIRS

        raise ValueError(f"Unsupported config type: {config_type}")

    def _validate_request(self, request: PriceRequest) -> None:
        if request.crypto_id not in binance_settings.SUPPORTED_PAIRS:
            raise ValueError(f"Unsupported cryptocurrency pair: {request.crypto_id}")
        if request.interval not in binance_settings.TIME_RANGES:
            raise ValueError(f"Invalid interval: {request.interval}")
        if request.data_type not in binance_settings.DATA_TYPES:
            raise ValueError(f"Invalid chart type: {request.data_type}")

    # Helper functions for API caller to have better format
    def _format_data(self, data: str, data_type: str) -> dict:
        # slalable for other data types. current implementation only has
        # klines. If you plan to add other binance data, you need to
        # add another format method.
        json_data = json.loads(data)
        match data_type:
            case "klines":
                return [OHLCData.from_binance(price_entry) for price_entry in json_data]
