from datetime import datetime

from pydantic import BaseModel


class RedisCacheble(BaseModel):
    def construct_key(self) -> str:
        raise NotImplementedError

    def separate_strings_with_colons(self, *parameters: list[str]) -> str:
        key = ""
        for index, parameter in enumerate(parameters):
            key += f"{parameter}:" if index < len(parameters) - 1 else parameter
        return key


class PriceTicker(RedisCacheble):
    crypto_id: int | None = None
    crypto_name: str
    exchange_name: str
    interval: str = "1h"


class BatchStatusResponse(BaseModel):
    """Response model for batch processing status."""

    crypto_name: str
    exchange: str
    interval: str
    cached: bool
    spread_computed: bool
    saved_to_db: bool


class ComputedSpreadResponse(BaseModel):
    """Response model for computed spreads with exchange names resolved."""

    crypto_name: str
    time: datetime | None
    spread_percent: float
    high_exchange: str
    low_exchange: str


class TaskStatusResponse(BaseModel):
    """Response model for background task initiation."""

    status: str
    message: str
