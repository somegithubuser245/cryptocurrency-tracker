from pydantic import BaseModel
from datetime import datetime
from enum import Enum

# class ChartType(Enum):
#     MARKET_CHART = "market_chart"
#     OHLC = "ohlc"

# class OHLC(BaseModel):
#     timestamp: datetime
#     open: float
#     high: float
#     low: float
#     close: float

# class SimplePrice(BaseModel):
#     timestamp: datetime
#     price: int

class PriceRequest(BaseModel):
    crypto_id: str
    days: int = 7
    chart_type: str = "ohlc"