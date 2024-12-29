from gecko import CryptoFetcher
from caching import Cacher
from models import PriceRequest
from datetime import datetime
from config import logger

class ApiCallManager:
    def __init__(self):
        self.data_fetcher = CryptoFetcher()
        self.redis_cacher = Cacher()
    
    async def get_price_stats(self, request: PriceRequest):
        if request.days > 365:
            logger.debug('Standard demo only has access to 365 days, none more')
            return
        
        raw_data = self.redis_cacher.get(request) # look if request is already cached and return it if so
        if raw_data is not None:
            return self.format_data(raw_data, request.chart_type)
        
        
        response = await self.data_fetcher.getResponse(request)
        raw_data = response.json()
        logger.debug('Testing out logger')

        self.redis_cacher.set(raw_data, request) # cache the response

        return self.format_data(raw_data, request.chart_type) # return to API caller in readable format

    def format_data(self, data, chart_type : str):
        if chart_type == "market_chart":
            return self.format_data_market_chart(data)
        
        return self.format_data_ohlc(data)


    # Helper functions for API caller to have better format
    def format_data_market_chart(self, data):
        formatted_data = [{
                "datetime": datetime.fromtimestamp(timestamp/1000).strftime('%Y-%m-%d %H:%M:%S'),
                "price": price
            } for timestamp, price in data["prices"]]

        return formatted_data

    def format_data_ohlc(self, data):
        formatted_data = []
        for entry in data:
            timestamp, open_price, high, low, close = entry
            formatted_data.append({
                "timestamp": timestamp,
                "open": open_price,
                "high": high,
                "low": low,
                "close": close
            })
        
        return formatted_data

        