import pandas as pd

from data_handling.timeframes_equalizer import TimeframeSynchronizer
from routes.models.schemas import PriceTickerRequest
from services.data_gather import DataManager
from data_handling.spread_object import Spread


class SpreadCalculator:
    def __init__(
            self,
            data_manager: DataManager,
            timeframe_synchronizer: TimeframeSynchronizer
    ) -> None:
        self.data_manager = data_manager
        self.synchronizer = timeframe_synchronizer

    async def create(self, pair: PriceTickerRequest) -> Spread:
        # gathering needed data
        requests_list = await self.generate_requests(pair)
        ohlc_all_supported = await self.data_manager.get_ohlc_data_cached(requests_list)
        
        aligned = self.synchronizer.sync_many(list(ohlc_all_supported.values()))
        exchange_names = self.generate_exchange_names(requests_list)

        return Spread(
            pair_name=pair.crypto_id,
            raw_frames=aligned,
            exchange_names=exchange_names
        )

    # helper functions
    async def generate_requests(
        self,
        pair: PriceTickerRequest,
    ) -> list[PriceTickerRequest]:
        arbitrable_pairs = await self.data_manager.get_arbitrable_pairs()
        supported_exchanges = arbitrable_pairs.get(pair.crypto_id)
        
        requests_list = [
            PriceTickerRequest(
                crypto_id=pair.crypto_id,
                interval=pair.interval,
                api_provider=exchange
            ) for exchange in supported_exchanges
        ]

        return requests_list
    
    def generate_exchange_names(
        self,
        reqeusts: list[PriceTickerRequest]
    ) -> list[str]:
        return [request.api_provider.value for request in reqeusts]
    
    
        
