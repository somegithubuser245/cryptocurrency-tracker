from pydantic import BaseModel

from app.config.config import SUPPORTED_EXCHANGES, SUPPORTED_PAIRS, TIME_RANGES, Exchange

config_types: dict[str, dict] = {
    "timeranges": TIME_RANGES,
    "pairs": SUPPORTED_PAIRS,
    "exchanges": SUPPORTED_EXCHANGES,
}

class CompareRequest(BaseModel):
    exchange1: Exchange
    exchange2: Exchange
    crypto_id: str
    interval: str = "1h"

class KlinesRequest(BaseModel):
    crypto_id: str
    interval: str = "1h"
    api_provider: Exchange
