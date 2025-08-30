import logging

from config.config import SUPPORTED_EXCHANGES, TickerType
from data_handling.exchanges_symbols_converter import Converter
from data_handling.timeframes_equalizer import TimeframeSynchronizer
from routes.models.schemas import CompareRequest, PriceTicker
from services.data_gather import DataManager
from services.external_api_caller import CryptoFetcher

logger = logging.getLogger(__name__)
class ApiCallManager():
    """Main class that handles calls from FastAPI"""

    def __init__(
        self,
        equalizer: TimeframeSynchronizer,
        converter: Converter,
        fetcher: CryptoFetcher,
        data_manager: DataManager
    ) -> None:
        self.equalizer = equalizer
        self.converter = converter
        self.fetcher = fetcher
        self.data_manager = data_manager

    async def get_timeframe_aligned(
        self, request: CompareRequest, type: TickerType
    ) -> dict[str, dict[str, float | int]]:
        exchanges = [request.exchange1, request.exchange2]

        requests = [
            PriceTicker(
                crypto_id=request.crypto_id, interval=request.interval, api_provider=exchange
            )
            for exchange in exchanges
        ]

        data_sets_raw = await self.data_manager.get_ohlc_data_cached(requests)

        column_names = self.equalizer.cnames
        columns_to_drop = column_names[-1] if type == TickerType.OHLC else column_names[2:]

        exchange_1_name, exchange_2_name = request.exchange1.value, request.exchange2.value

        aligned_timeseries1, aligned_timeseries2 = self.equalizer.sync_two(
            data_sets_raw.get(requests[0].construct_key()),
            data_sets_raw.get(requests[1].construct_key()),
            columns_to_drop
        )

        return {
            exchange_1_name: aligned_timeseries1,
            exchange_2_name: aligned_timeseries2
        }

    async def get_arbitrable_pairs(self) -> dict[str, list[str]]:
        exchanges = await self.fetcher.get_exchanges_with_markets(SUPPORTED_EXCHANGES.values())
        return self.converter.get_list_like(exchanges)
