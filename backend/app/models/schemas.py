from pydantic import BaseModel
from app.config.config import logger, ApiProvider, TIME_RANGES, SUPPORTED_PAIRS

config_types: dict[str, dict] = {
    "timeranges": TIME_RANGES,
    "pairs": SUPPORTED_PAIRS
}

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
    def from_external_api(cls, data_entry: dict) -> dict:
        return cls(
            time = data_entry[0] / 1000,
            open = float(data_entry[1]),
            high = float(data_entry[2]),
            low = float(data_entry[3]),
            close = float(data_entry[4])
        ).model_dump()