import logging

import redis
from config.config import RedisSettings

logger = logging.getLogger(__name__)


class RedisClient:
    def __init__(self) -> None:
        self.client: redis.Redis | None = self._init_client()

    def set(self, key: str, data: str, ttl: int) -> None:
        if not self.client:
            return
        logger.info(f"Caching data for key: {key} with TTL: {ttl / 60} minutes")
        self.client.set(name=key, value=data, ex=ttl)

    def get(self, key: str) -> str | None:
        if not self.client:
            return None

        response = self.client.get(key)

        if response:
            logger.info(f"Cache hit for key: {key}")
            return response
        return None

    def _init_client(self) -> redis.Redis | None:
        r_config = RedisSettings()
        return redis.Redis(
            host=r_config.REDIS_HOST, port=r_config.REDIS_PORT, db=r_config.REDIS_DB
        )

    def healthcheck(self) -> bool:
        if not self.client:
            return False
        try:
            self.client.set("health", "true", 1)
            return self.client.get("health") == b"true"
        except (redis.RedisError, redis.TimeoutError) as e:
            logger.error(f"REDIS CLIENT UNAVAILABLE: {e}")
            return False
