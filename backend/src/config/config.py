from enum import Enum, StrEnum, auto

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """This is a pydantic settings class
    You can define your own .env
    If not, pydantic defaults
    to values defined here"""

    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0


settings = Settings()


CACHE_TTL_CONFIG: dict = {
    "5m": 300,
    "30m": 1800,
    "1h": 3600,
    "4h": 14400,
    "1d": 86400,
    "1w": 604800,
    "1M": 604800,
}


class Exchange(StrEnum):
    BINANCE = "binance"
    OKX = "okx"
    BYBIT = "bybit"
    MEXC = "mexc"
    BINGX = "bingx"
    GATEIO = "gateio"
    KUCION = "kucoin"


class TickerType(StrEnum):
    OHLC = auto()
    CHART_LINE = auto()


SUPPORTED_EXCHANGES: dict = {entry: entry.value for entry in Exchange}

# used for frontend
TIME_RANGES: dict = {
    "5m": "5 minutes",
    "30m": "30 minutes",
    "1h": "Hourly",
    "4h": "4 Hours",
    "1d": "Daily",
    "1w": "Weekly",
    "1M": "Monthly",
}
