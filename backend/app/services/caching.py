import redis
from app.models.schemas import PriceRequest
from app.config.config import settings, logger

class Cacher():
    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST, 
            port=settings.REDIS_PORT, 
            db=settings.REDIS_DB)

    def set(self, data, request: PriceRequest, ttl: int):
        key = self.construct_key(request)
        logger.info(f"Caching data for key: {key} with TTL: {ttl / 60} minutes")
        self.redis_client.set(name=key, value=data, ex=ttl)

    def get(self, request: PriceRequest):
        key = self.construct_key(request)
        response = self.redis_client.get(key)

        if response:
            logger.info(f"Cache hit for key: {key}") 
            return response
        return None

    def construct_key(self, reqest: PriceRequest) -> str:
        return f"{reqest.data_type}:{reqest.crypto_id}:{reqest.interval}"

