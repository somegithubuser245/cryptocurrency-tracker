import logging
from pydantic_settings import BaseSettings

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

