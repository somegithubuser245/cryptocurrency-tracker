from typing import Annotated
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from gecko import CryptoFetcher

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:6379"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

cryptoFetcher = CryptoFetcher()
    
@app.get("/api/crypto/{crypto_id}/{chart_type}")
async def get_data(
    crypto_id: str,
    days: Annotated[int, Query(gt = 0, lt=365)] = 7,
    chart_type: str = "ohlc",
):
    try:
        data = await cryptoFetcher.get_price_stats(crypto_id, days, chart_type)
        return data
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


