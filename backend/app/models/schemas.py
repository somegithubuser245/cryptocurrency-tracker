from pydantic import BaseModel
from app.config.config import logger, ApiProvider

class KlinesRequest(BaseModel):
    crypto_id: str
    interval: str = '1h'
    api_provider: ApiProvider

class OHLCData(BaseModel):
    close: float
    high: float
    low: float
    open: float
    time: int

    @classmethod
    def from_external_api(cls, api_name: ApiProvider, data_entry: dict) -> dict:
        match api_name:
            case ApiProvider.BINANCE:
                return cls.from_binance(data_entry)
            case ApiProvider.OKX:
                return cls.from_okx(data_entry)
            
    @classmethod
    def from_binance(cls, data_entry: dict) -> dict:
        return cls(
            time = data_entry[0] / 1000,
            open = data_entry[1],
            high = data_entry[2],
            low = data_entry[3],
            close = data_entry[4]
        ).model_dump()
    
    @classmethod
    def from_okx(cls, data_entry: dict) -> dict:
        return cls(
            time = int(data_entry[0]) / 1000,
            open = data_entry[1],
            high = data_entry[2],
            low = data_entry[3],
            close = data_entry[4]
        ).model_dump()
