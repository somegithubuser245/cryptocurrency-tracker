import logging

import redis
from config.config import RedisSettings

logger = logging.getLogger(__name__)


class RedisClient:
    def __init__(self) -> None:
        self.available = self._init_client()

    def set(self, key: str, data: str, ttl: int) -> None:
        if not self.available:
            return
        logger.info(f"Caching data for key: {key} with TTL: {ttl / 60} minutes")
        self.redis_client.set(name=key, value=data, ex=ttl)

    def get(self, key: str) -> str | None:
        if not self.available:
            return None

        response = self.redis_client.get(key)

        if response:
            logger.info(f"Cache hit for key: {key}")
            return response
        return None

    def _init_client(self) -> bool:
        r_config = RedisSettings()
        self.redis_client = redis.Redis(
            host=r_config.REDIS_HOST, port=r_config.REDIS_PORT, db=r_config.REDIS_DB
        )
        if not self.healthcheck():
            self.redis_client = None
            return False
        return True

    def healthcheck(self) -> bool:
        try:
            self.redis_client.set("health", "true", 1)
            return self.redis_client.get("health") == b"true"
        except (redis.RedisError, redis.TimeoutError) as e:
            logger.error(f"REDIS CLIENT UNAVAILABLE: {e}")
            return False
