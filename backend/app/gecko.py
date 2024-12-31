import os
import httpx

from config import COINGECKO_API_URL
from models import PriceRequest
from dotenv import load_dotenv

class CryptoFetcher:
    def __init__(self):
        load_dotenv()
        self.client = httpx.AsyncClient()
        self.base_url = COINGECKO_API_URL
        self.api_key = os.getenv("COINGECKO_API_KEY")
        self.headers = {
            "x-cg-demo-api-key": self.api_key
        }
            
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
    

        
                
            

            
