import redis
from config.config import logger, settings
from routes.models.schemas import RedisCacheble


class Cacher:
    def __init__(self) -> None:
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB
        )

    def set(self, data: str, request: RedisCacheble, ttl: int) -> None:
        key = request.construct_key()
        logger.info(f"Caching data for key: {key} with TTL: {ttl / 60} minutes")
        self.redis_client.set(name=key, value=data, ex=ttl)

    def get(self, request: RedisCacheble) -> str:
        key = request.construct_key()
        response = self.redis_client.get(key)

        if response:
            logger.info(f"Cache hit for key: {key}")
            return response
        return None
    
    def _init_client(self) -> bool:
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB
        )
        if not self.healthcheck():
            self.redis_client = None
            return False
        return True
        
    def healthcheck(self) -> bool:
        try:
            self.redis_client.set("health", "true", 1)
            return "true" == self.redis_client.get("health")
        except (redis.RedisError, redis.TimeoutError) as e:
            logger.error("REDIS CLIENT UNAVAILABLE")
            return False
