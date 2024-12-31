from pydantic import BaseModel
from datetime import datetime

class PriceRequest(BaseModel):
    crypto_id: str
    interval: str = '1h'
    chart_type: str = "ohlc"