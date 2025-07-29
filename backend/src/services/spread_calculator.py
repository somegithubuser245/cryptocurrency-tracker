from data_handling.timeframes_equalizer import Equalizer
from routes.models.schemas import PriceTicketRequest
from services.data_gather import DataManager


class SpreadCalculator:
    def __init__(
            self,
            data_manager: DataManager,
            equalizer: Equalizer
    ) -> None:
        self.data_manager = data_manager
        self.equalizer = equalizer    

    async def calculate(self, pair: PriceTicketRequest) -> dict:
        arbitrable_pairs = await self.data_manager.get_arbitrable_pairs()
        requests_list = self.generate_requests(pair, arbitrable_pairs)
        ohlc_all_supported = await self.data_manager.get_ohlc_data_cached(requests_list)
        return ohlc_all_supported
        

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
    
    
        
