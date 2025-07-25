
from routes.models.schemas import PriceTicketRequest
from services.caching import Cacher
from services.external_api_caller import CryptoFetcher

import asyncio
import json


class DataManager:
    """
    This class is intended to manage cached data
    If there's cache, it will return it
    If not, it will make calls to fetch it
    """
    def __init__(self, redis_cacher: Cacher, fetcher: CryptoFetcher):
        self.redis_cacher=redis_cacher
        self.fetcher=fetcher

    async def get_ohlc_data_cached(self, requests: list[PriceTicketRequest]) -> list[list[list[float]]]:
        """
        This can be used in the future to implement batching-like data gathering
        For now, this functions main puprose is to fetch data using async from
        two requests
        """
        ohlc_dict = {request.construct_key(): None for request in requests}
        uncached_requests, ohlc_dict = self._fill_with_cached_get_uncached(
            ohlc_dict=ohlc_dict,
            requests=requests
        )
        
        if uncached_requests is None:
            return ohlc_dict
        
        ticker_data_responses = await asyncio.gather(*[
            self.fetcher.get_ohlc(request) for request in uncached_requests.values()
        ])

        for index, uncached_ticker_entry in enumerate(uncached_requests.items()):
            uncached_ticker_request_key, uncached_ticker_request = uncached_ticker_entry
            
            data_response = ticker_data_responses[index]
            ohlc_dict[uncached_ticker_request_key] = data_response
            
            self.redis_cacher.set(
                json.dumps(data_response),
                uncached_ticker_request,
                300)

        return list(ohlc_dict.values())

    def _fill_with_cached_get_uncached(
            self,
            ohlc_dict: dict,
            requests: list[PriceTicketRequest]
    ) -> tuple[dict, dict[str, list[list[float]]]]:
        """
        Fill main dict with cached ticker data, if any found
        Otherwise, expand the list to fetch data for uncached ticker requests
        """
        uncached = {}
        for ticker_request in requests:
            ticker_key = ticker_request.construct_key()
            cached = self.redis_cacher.get(ticker_request)
            
            if not cached:
                uncached[ticker_key] = ticker_request
                continue

            ohlc_dict[ticker_key] = json.loads(cached)

        return uncached, ohlc_dict