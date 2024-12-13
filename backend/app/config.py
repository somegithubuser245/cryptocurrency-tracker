from pydantic import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Crypto Analytics API"
    
    # CoinGecko Configuration
    COINGECKO_API_URL: str = "https://api.coingecko.com/api/v3"
    
    # Rate Limiting
    RATE_LIMIT_PER_MONTH: int = 30000
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()