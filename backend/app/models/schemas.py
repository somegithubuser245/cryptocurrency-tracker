from pydantic import BaseModel

class PriceRequest(BaseModel):
    crypto_id: str
    interval: str = '1h'
    data_type: str = "klines"