import logging
from pydantic_settings import BaseSettings

logger = logging.getLogger("uvicorn.error")

class Settings(BaseSettings):

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

settings = Settings()

