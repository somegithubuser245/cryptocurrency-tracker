import asyncio
import json

from config.config import SUPPORTED_EXCHANGES
from data_manipulation.exchanges_symbols_converter import Converter
from routes.models.schemas import PriceTicker
from services.caching import RedisClient
from services.external_api_caller import CryptoFetcher


class DataManager:
    """
    This class is intended to manage cached data
    If there's cache, it will return it
    If not, it will make calls to fetch it
    """

    def __init__(self, redis_cacher: RedisClient, fetcher: CryptoFetcher, converter: Converter):
        self.redis_cacher = redis_cacher
        self.fetcher = fetcher
        self.converter = converter

    async def get_ohlc_data_cached(
        self, requests: list[PriceTicker]
    ) -> dict[str, list[list[float]]]:
        """
        This can be used in the future to implement batching-like data gathering
        For now, this functions main purpose is to fetch data using async from
        two requests
        """
        ohlc_dict = {request.construct_key(): None for request in requests}
        uncached_requests, ohlc_dict = self._fill_with_cached_get_uncached(
            ohlc_dict=ohlc_dict, requests=requests
        )

        if not uncached_requests:
            return ohlc_dict

        tasks = [(self.fetcher.get_ohlc(request)) for request in requests]
        ticker_data_responses = await asyncio.gather(*tasks, return_exceptions=True)

        for index, uncached_ticker_request in enumerate(uncached_requests):
            data_response = ticker_data_responses[index]
            uncached_request_key = uncached_ticker_request.construct_key()

            if not data_response:
                ohlc_dict.pop(uncached_request_key)
                continue

            ohlc_dict[uncached_request_key] = data_response

            self.redis_cacher.set(json.dumps(data_response), uncached_ticker_request, 10000)

        return ohlc_dict

    def _fill_with_cached_get_uncached(
        self, ohlc_dict: dict, requests: list[PriceTicker]
    ) -> tuple[list[PriceTicker], dict[str, list[list[float]]]]:
        """
        Fill main dict with cached ticker data, if any found
        Otherwise, expand the list to fetch data for uncached ticker requests
        """
        uncached = []
        for ticker_request in requests:
            ticker_key = ticker_request.construct_key()
            cached = self.redis_cacher.get(ticker_request)

            if not cached:
                uncached.append(ticker_request)
                continue

            ohlc_dict[ticker_key] = json.loads(cached)

        return uncached, ohlc_dict

    async def get_arbitrable_pairs(self) -> dict[str, list[str]]:
        exchanges = await self.fetcher.get_exchanges_with_markets(SUPPORTED_EXCHANGES.values())
        return self.converter.get_list_like(exchanges)
