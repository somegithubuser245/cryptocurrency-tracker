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

    async def calculate(self, pair: PriceTicketRequest) -> dict:
        # gathering needed data
        requests_list = await self.generate_requests(pair)
        ohlc_all_supported = await self.data_manager.get_ohlc_data_cached(requests_list)
        
        aligned = self.synchronizer.sync_many(list(ohlc_all_supported.values()))
        
        multiindex_ohlc = pd.concat(aligned, keys=self.generate_exchange_names(requests_list)).unstack(level=0)
        spreads_df = multiindex_ohlc["close"].apply(self.calculate_max_spread, axis=1)

        spreads_df = pd.DataFrame.from_records(
            spreads_df, 
            columns=["spread", "spread_percent", "high_exchange", "low_exchange"],
            index=spreads_df.index
        ).reset_index()
        
        max_timestamp = spreads_df["spread"].idxmax()
        return spreads_df.loc[max_timestamp].to_dict()
    
    def calculate_max_spread(self, x: pd.Series):
        exchange_names = x.index.to_list()
        name1 = exchange_names[0]
        max_exchange_name, min_exchange_mane = name1, name1
        
        entry1 = x.iloc[0]
        max, min = entry1, entry1
        
        for i in range(1, len(x)):
            price_entry = x.iloc[i]
            if price_entry < min:
                min = price_entry
                min_exchange_mane = exchange_names[i]

            if price_entry > max:
                max = price_entry
                max_exchange_name = exchange_names[i]
    
        spread = max - min
        spread_percent = spread / ((max + min) / 2) * 100
        return spread, spread_percent, max_exchange_name, min_exchange_mane


    # helper functions
    async def generate_requests(
        self,
        pair: PriceTicketRequest,
    ) -> list[PriceTicketRequest]:
        arbitrable_pairs = await self.data_manager.get_arbitrable_pairs()
        supported_exchanges = arbitrable_pairs.get(pair.crypto_id)
        
        requests_list = [
            PriceTicketRequest(
                crypto_id=pair.crypto_id,
                interval=pair.interval,
                api_provider=exchange
            ) for exchange in supported_exchanges
        ]

        return requests_list
    
    def generate_exchange_names(
        self,
        reqeusts: list[PriceTicketRequest]
    ) -> list[str]:
        return [request.api_provider.value for request in reqeusts]
    
    
        
