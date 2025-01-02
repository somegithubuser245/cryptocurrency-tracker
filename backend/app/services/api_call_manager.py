from .binance import CryptoFetcher
from .caching import Cacher
from app.models.schemas import PriceRequest
from app.config.binance_config import SUPPORTED_PAIRS, TIME_RANGES

class ApiCallManager:
    def __init__(self):
        self.data_fetcher = CryptoFetcher()
        self.redis_cacher = Cacher()
    
    async def get_price_stats(self, request: PriceRequest):
        raw_data = self.redis_cacher.get(request) # look if request is already cached and return it if so
        if raw_data is not None:
            return self.format_data(raw_data, request.chart_type)
        
        response = await self.data_fetcher.get_response(request)
        raw_data = response.json()

        self.redis_cacher.set(raw_data, request) # cache the response

        return self.format_data(raw_data, request.chart_type) # return to API caller in readable format

    def format_data(self, data, chart_type : str):
        if chart_type == "market_chart":
            return self.format_data_market_chart(data)
        
        return self.format_data_ohlc(data)
    
    def get_config_data(self, config_data: str):
        if config_data == 'timeranges':
            return TIME_RANGES
        
        return SUPPORTED_PAIRS

    # Helper functions for API caller to have better format
    def format_data_ohlc(self, data):
        formatted_data = []
        for entry in data:
            formatted_data.append({
                "timestamp": entry[0],
                "open": float(entry[1]),
                "high": float(entry[2]),
                "low": float(entry[3]),
                "close": float(entry[4])
            })

        
        return formatted_data
        