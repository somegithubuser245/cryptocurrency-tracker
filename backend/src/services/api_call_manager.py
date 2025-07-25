import asyncio
from functools import lru_cache
from typing import Annotated

from config.config import SUPPORTED_EXCHANGES, TickerType
from data_handling.exchanges_symbols_converter import Converter
from data_handling.timeframes_equalizer import Equalizer
from fastapi import Depends
from routes.models.schemas import CompareRequest, PriceTicketRequest
from services.caching import Cacher
from services.data_gather import DataManager
from services.external_api_caller import CryptoFetcher


class ApiCallManager():
    """Main class that handles calls from FastAPI"""

    def __init__(self) -> None:
        self.equalizer = Equalizer()
        self.converter = Converter()
        self.fetcher = CryptoFetcher()
        self.redis_cacher = Cacher()
        self.data_manager = DataManager(
            self.redis_cacher,
            self.fetcher
        )

    async def get_timeframe_aligned(
        self, request: CompareRequest, type: TickerType
    ) -> dict[str, dict[str, float | int]]:
        exchanges = [request.exchange1, request.exchange2]

        requests = [
            PriceTicketRequest(
                crypto_id=request.crypto_id, interval=request.interval, api_provider=exchange
            )
            for exchange in exchanges
        ]

        data_sets_raw = await self.data_manager.get_ohlc_data_cached(requests)

        column_names = self.equalizer.cnames
        columns_to_drop = column_names[-1] if type == TickerType.OHLC else column_names[2:]

        eq_data_exchange1, eq_data_exchange2 = self.equalizer.equalize_timeframes(
            data_sets_raw[0], data_sets_raw[1], columns_to_drop
        )

        return {
            request.exchange1.value: eq_data_exchange1,
            request.exchange2.value: eq_data_exchange2,
        }

    async def get_arbitrable_pairs(self) -> dict[str, list[str]]:
        exchanges = await self.fetcher.get_exchanges_with_markets(SUPPORTED_EXCHANGES.values())
        return self.converter.get_list_like(exchanges)


# Caches the instance and provides singletone pattern
@lru_cache
def get_api_call_manager() -> ApiCallManager:
    return ApiCallManager()


call_manager_dependency = Annotated[ApiCallManager, Depends(get_api_call_manager)]
