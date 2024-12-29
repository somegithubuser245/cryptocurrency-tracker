from typing import Annotated
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from api_call_manager import ApiCallManager
from models import PriceRequest

# Setup
app = FastAPI()
api_call_manager = ApiCallManager()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:6379"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/crypto/{crypto_id}/{chart_type}")
async def get_data(
    crypto_id: str,
    days: Annotated[int, Query(gt = 0, lt=365)] = 7,
    chart_type: str = "ohlc",
):
    try:
        request = PriceRequest(crypto_id=crypto_id, days=days, chart_type=chart_type)
        data = await api_call_manager.get_price_stats(request)
        return data
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


