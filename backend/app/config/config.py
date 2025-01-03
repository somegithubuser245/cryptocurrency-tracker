import logging
from pydantic_settings import BaseSettings

logger = logging.getLogger("uvicorn.error")

class Settings(BaseSettings):
    # market-data only API
    BINANCE_API_URL: str = "https://data-api.binance.vision/api/v3"

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

settings = Settings()

