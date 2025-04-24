import logging
from pydantic_settings import BaseSettings
from enum import Enum, auto

# most straightforward way to show logs in uvicorn
logger = logging.getLogger("uvicorn.error")

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
    "1H": 3600,
    "4H": 14400,
    "1D": 86400,
    "1w": 604800,
    "1M": 604800,
}

class ApiProvider(str, Enum):
    BINANCE = "binance"
    OKX = "okx"

# used for frontend
TIME_RANGES: dict = {
    "5m": "5 minutes",
    "30m": "30 minutes",
    "1H": "Hourly",
    "4H": "4 Hours",
    "1D": "Daily",
    "1W": "Weekly",
    "1M": "Monthly"
}

SUPPORTED_PAIRS: dict = {
    'BTCUSDT': 'Bitcoin',
    'ETHUSDT': 'Ethereum',
    'SOLUSDT': 'Solana',
    'ADAUSDT': 'Cardano',
    'AVAXUSDT': 'Avalanche',
    'DOTUSDT': 'Polkadot'
}

