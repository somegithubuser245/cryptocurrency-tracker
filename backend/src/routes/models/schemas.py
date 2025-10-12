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


class BatchStatusSummaryResponse(BaseModel):
    """Aggregate batch processing status summary."""

    total_pairs: int
    cached: int
    spreads_computed: int
    processing_progress: float


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
