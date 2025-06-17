import redis

from app.config.config import logger, settings
from app.models.schemas import PriceTicketRequest


class Cacher:
    def __init__(self) -> None:
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB
        )

    def set(self, data: str, request: PriceTicketRequest, ttl: int) -> None:
        key = self.construct_key(request)
        logger.info(f"Caching data for key: {key} with TTL: {ttl / 60} minutes")
        self.redis_client.set(name=key, value=data, ex=ttl)

    def get(self, request: PriceTicketRequest) -> str:
        key = self.construct_key(request)
        response = self.redis_client.get(key)

        if response:
            logger.info(f"Cache hit for key: {key}")
            return response
        return None

    def construct_key(self, reqest: PriceTicketRequest) -> str:
        return f"{reqest.api_provider}:{reqest.crypto_id}:{reqest.interval}"
