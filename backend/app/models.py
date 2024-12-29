from pydantic import BaseModel
from datetime import datetime

class OHLC(BaseModel):
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float

class SimplePrice(BaseModel):
    timestamp: datetime
    price: int