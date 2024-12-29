from fastapi import HTTPException, logger
import httpx
from datetime import datetime
from time import time
import os
from dotenv import load_dotenv

class CryptoFetcher:
    def __init__(self):
        load_dotenv()
        self.client = httpx.AsyncClient()
        self.base_url = os.getenv("COINGECKO_API_URL")
        self.api_key = os.getenv("COINGECKO_API_KEY")
        self.headers = {
            "x-cg-demo-api-key": self.api_key
        }

    async def get_price_stats(self, coin_id: str, days: int = 7, type: str = "market_chart"):
        if days > 365:
            raise ValueError("Free tier only 365 days of historical data. Pay money, bitch!")

        try:
            response = await self.getResponse(days, coin_id, type)
            data = response.json()

            if response.status_code == 429:
                raise HTTPException(status_code=429, detail="Rate limit exceeded")
            
            if type == "market_chart":
                return self.format_data_market_chart(data)
            
            return self.format_data_ohlc(data)

        except Exception as e:
            raise HTTPException(status_code=500, detail = str(e))
        
    async def getResponse(self, days: int, coin_id: str, type: str):
        url = f"{self.base_url}/coins/{coin_id}/{type}"

        params = {
            "vs_currency" : "usd",
            "days" : days,
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
    

        
                
            

            
