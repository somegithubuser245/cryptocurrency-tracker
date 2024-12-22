import asyncio
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
        self.base_url = "https://api.coingecko.com/api/v3"
        self.api_key = os.getenv("COINGECKO_API_KEY")
        self.headers = {
            "x-cg-demo-api-key": self.api_key
        }

    async def get_price_history(self, coin_id: str, days: int = 7):
        if days > 365:
            raise ValueError("Free tier only 365 days of historical data. Pay money, bitch!")

        try:
            url = f"{self.base_url}/coins/{coin_id}/market_chart"
            params = {
                "vs_currency" : "usd",
                "days" : days,
            }

            response = await self.client.get(
                url, 
                headers = self.headers, 
                params =  params)
            

            data = response.json()

            if response.status_code == 429:
                raise HTTPException(status_code=429, detail="Rate limit exceeded")
            
            formatted_data = [{
                "datetime": datetime.fromtimestamp(timestamp/1000).strftime('%Y-%m-%d %H:%M:%S'),
                "price": price
            } for timestamp, price in data["prices"]]

            return formatted_data
            
            

        except Exception as e:
            raise HTTPException(status_code=500, detail = str(e))
        
                
            

            
