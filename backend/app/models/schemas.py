from pydantic import BaseModel

class PriceRequest(BaseModel):
    crypto_id: str
    interval: str = '1h'
    data_type: str = "klines"

class OHLCData(BaseModel):
    close: float
    high: float
    low: float
    open: float
    time: int

    @classmethod
    def from_binance(cls, data_entry: dict) -> dict:
        return cls(
            time = data_entry[0] / 1000,
            open = data_entry[1],
            high = data_entry[2],
            low = data_entry[3],
            close = data_entry[4]
        ).model_dump()