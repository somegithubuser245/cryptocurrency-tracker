import pandas as pd

from data_handling.timeframes_equalizer import TimeframeSynchronizer
from routes.models.schemas import PriceTicketRequest
from services.data_gather import DataManager


class SpreadCalculator:
    def __init__(
            self,
            data_manager: DataManager,
            timeframe_synchronizer: TimeframeSynchronizer
    ) -> None:
        self.data_manager = data_manager
        self.synchronizer = timeframe_synchronizer

        self.cnames = ["time", "open", "high", "low", "close", "volume"]

    async def calculate(self, pair: PriceTicketRequest) -> dict:
        arbitrable_pairs = await self.data_manager.get_arbitrable_pairs()
        requests_list = self.generate_requests(pair, arbitrable_pairs)
        
        ohlc_all_supported = await self.data_manager.get_ohlc_data_cached(requests_list)
        
        aligned = self.synchronizer.sync_many(list(ohlc_all_supported.values()))
        
        # you can access each exchange's entries by specifying its name
        # e.g. multiindex_ohlc["binance"]
        multiindex_ohlc = pd.concat(aligned, keys=self.generate_exchange_names(requests_list)).stack()

        return {}
    
    def generate_requests(
        self,
        pair: PriceTicketRequest,
        arbitrable_pairs: dict[str, list[str]]
    ) -> list[PriceTicketRequest]:
        crypto_id = pair.crypto_id
        interval = pair.interval
        supported_exchanges = arbitrable_pairs.get(crypto_id)
        requests_list = [
            PriceTicketRequest(
                crypto_id=crypto_id,
                interval=interval,
                api_provider=exchange
            ) for exchange in supported_exchanges
        ]

        return requests_list
    
    def generate_exchange_names(
        self,
        reqeusts: list[PriceTicketRequest]
    ) -> list[str]:
        return [request.api_provider.value for request in reqeusts]
    
    
        
