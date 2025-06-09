import json
import logging

from app.services.timeframes_equalizer import Equalizer

from app.config import config
from app.config.config import logger
from app.models.schemas import CompareRequest, KlinesRequest, OHLCData

from .caching import Cacher
from .external_api_caller import CryptoFetcher


class ApiCallManager:
    """Main class that handles calls from FastAPI"""

    def __init__(self) -> None:
        self.data_fetcher = CryptoFetcher()
        self.equalizer = Equalizer()
        self.redis_cacher = Cacher()

    def get_timeframe_aligned(self, request: CompareRequest) -> dict[str, dict[str, float | int]]:
        requests = [
            KlinesRequest(
                crypto_id=request.crypto_id,
                interval=request.interval,
                api_provider=request.exchange1,
            ),
            KlinesRequest(
                crypto_id=request.crypto_id,
                interval=request.interval,
                api_provider=request.exchange2,
            ),
        ]
        data_sets_raw = [self.data_fetcher.get_response(value) for value in requests]
        data_set1, data_set2 = self.equalizer.equalize_timeframes(
            data_sets_raw[0], data_sets_raw[1]
        )

        return {request.exchange1.value: data_set1, request.exchange2.value: data_set2}

    def get_price_stats(self, request: KlinesRequest) -> dict:
        # look if request is already cached and return it if so
        raw_data = self.redis_cacher.get(request)
        if raw_data:
            return self._format_data(raw_data, request)

        # if not, make request to external api
        raw_data = self.data_fetcher.get_response(request)
        # cache response
        ttl = config.CACHE_TTL_CONFIG[request.interval]
        self.redis_cacher.set(raw_data, request, ttl)

        # return to API caller in readable format
        return self._format_data(raw_data, request)

    # Helper functions for API caller to have better format
    def _format_data(self, data: str, request: KlinesRequest) -> dict:
        # slalable for other data types. current implementation only has
        # klines. If you plan to add other binance data, you need to
        # add another format method
        json_data = json.loads(data)

        return [OHLCData.from_external_api(price_entry) for price_entry in json_data]
