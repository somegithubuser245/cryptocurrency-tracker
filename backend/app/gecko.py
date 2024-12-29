from fastapi import HTTPException
import httpx
from datetime import datetime
from time import time
import os
from dotenv import load_dotenv
from caching import Cacher
from logger_config import setup_logger
from models import PriceRequest

logger = setup_logger()

class CryptoFetcher:
    def __init__(self):
        load_dotenv()
        self.r = Cacher()
        self.client = httpx.AsyncClient()
        self.base_url = os.getenv("COINGECKO_API_URL")
        self.api_key = os.getenv("COINGECKO_API_KEY")
        self.headers = {
            "x-cg-demo-api-key": self.api_key
        }

    async def get_price_stats(self, reqest: PriceRequest):
        if reqest.days > 365:
            raise ValueError("Free tier only 365 days of historical data. Pay money, bitch!")

        try:
            cache = self.getCache(reqest)
            if cache is not None:
                logger.debug("Cache is accepted and returned") 
                return self.format_data_ohlc(cache)

            response = await self.getResponse(reqest)
            data = response.json()

            if response.status_code == 429:
                raise HTTPException(status_code=429, detail="Rate limit exceeded")
            
            if reqest.chart_type == "market_chart":
                return self.format_data_market_chart(data)
            
            
            formatted_data = self.format_data_ohlc(data)
            self.setCache(data, reqest)
            return formatted_data

        except Exception as e:
            raise HTTPException(status_code=500, detail = str(e))
        
    def getCache(self, request: PriceRequest):
        return self.r.get(request)


    def setCache(self, data, request: PriceRequest):
        try:
            logger.debug('Setting cache')
            self.r.set(data, request)
        except Exception as e:
            logger.debug(str(e))
            
        
    async def getResponse(self, request: PriceRequest):
        url = f"{self.base_url}/coins/{request.crypto_id}/{request.chart_type}"

        params = {
            "vs_currency" : "usd",
            "days" : request.days,
        }
        
        return await self.client.get(
                url, 
                headers = self.headers,
                params =  params)
    
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
    

        
                
            

            
