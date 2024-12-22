from typing import Annotated
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

from . import gecko

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

cryptoFetcher = gecko.CryptoFetcher()

@app.get("/api/crypto/{crypto_id}/history")
async def get_crypto_history(
        crypto_id: str,
        days: int = 7
):
    try:
        data = await cryptoFetcher.get_price_history(crypto_id, days)
        return {
            "crypto_id" : crypto_id,
            "data" : data,
            "granularity": "5-minute" if days == 1 else "hourly" if days <= 90 else "daily"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))



