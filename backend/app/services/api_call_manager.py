from .binance import CryptoFetcher
from .caching import Cacher
from app.models.schemas import PriceRequest
from app.config.binance_config import binance_settings

class ApiCallManager:
    def __init__(self):
        self.data_fetcher = CryptoFetcher()
        self.redis_cacher = Cacher()
    
    async def get_price_stats(self, request: PriceRequest):
        self._validate_request(request)
        
        # look if request is already cached and return it if so
        raw_data = self.redis_cacher.get(request) 
        if raw_data is not None:
            return self.format_data(raw_data, request.chart_type)
        
        response = await self.data_fetcher.get_response(request)
        raw_data = response.json()

        self.redis_cacher.set(raw_data, request) # cache the response

        # return to API caller in readable format
        return self.format_data(raw_data, request.chart_type) 

    def get_config_data(self, config_data: str):
        if config_data == 'timeranges':
            return binance_settings.TIME_RANGES
        
        return binance_settings.SUPPORTED_PAIRS
    
    def _validate_request(self, request: PriceRequest) -> None:
        if request.crypto_id not in binance_settings.SUPPORTED_PAIRS:
            raise ValueError(f"Unsupported cryptocurrency pair: {request.crypto_id}")
        if request.interval not in binance_settings.TIME_RANGES:
            raise ValueError(f"Invalid interval: {request.interval}")
        if request.chart_type not in ["ohlc", "market_chart"]:
            raise ValueError(f"Invalid chart type: {request.chart_type}")

    # Helper functions for API caller to have better format
    def format_data(self, data, chart_type : str):
        if chart_type == "market_chart":
            return self.format_data_market_chart(data)
        
        return self.format_data_ohlc(data)
    
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
        