import asyncio

from config.config import TickerType
from data_handling.timeframes_equalizer import Equalizer
from routes.models.schemas import CompareRequest, PriceTicketRequest
from services.caching import Cacher
from services.external_api_caller import CryptoFetcher


class ApiCallManager:
    """Main class that handles calls from FastAPI"""

    def __init__(self) -> None:
        self.equalizer = Equalizer()
        self.redis_cacher = Cacher()
        self.fetcher = CryptoFetcher()

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

        data_sets_raw = await asyncio.gather(
            *[self.fetcher.get_ohlc(ticket_request) for ticket_request in requests]
        )

        column_names = list(self.equalizer.cnames)
        columns_to_drop = column_names[-1] if type == TickerType.OHLC else column_names[2:]

        eq_data_exchange1, eq_data_exchange2 = self.equalizer.equalize_timeframes(
            data_sets_raw[0], data_sets_raw[1], columns_to_drop
        )

        return {
            request.exchange1.value: eq_data_exchange1,
            request.exchange2.value: eq_data_exchange2,
        }
