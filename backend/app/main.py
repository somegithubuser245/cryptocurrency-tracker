from typing import Annotated
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from api_call_manager import ApiCallManager
from models import PriceRequest
from binance_config import SUPPORTED_PAIRS

# Setup
app = FastAPI()
api_call_manager = ApiCallManager()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/crypto/config/{config_data}")
async def get_pairs(
    config_data: str
):
    return api_call_manager.get_config_data(config_data)

@app.get("/api/crypto/{crypto_id}/{chart_type}")
async def get_data(
    crypto_id: str,
    interval: str = '4h',
    chart_type: str = "ohlc",
):
    try:
        request = PriceRequest(crypto_id=crypto_id, interval=interval, chart_type=chart_type)
        data = await api_call_manager.get_price_stats(request)
        return data
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    

