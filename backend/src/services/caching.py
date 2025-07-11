import redis
import logging
from ..config.config import logger, settings
from ..routes.models.schemas import PriceTicketRequest

logger = logging.getLogger(__name__)

class Cacher:
    def __init__(self) -> None:
        try:
            self.redis_client = redis.Redis(
                host=settings.REDIS_HOST, 
                port=settings.REDIS_PORT, 
                db=settings.REDIS_DB,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # Test connection
            self.redis_client.ping()
            logger.info(f"Redis connected successfully at {settings.REDIS_HOST}:{settings.REDIS_PORT}")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Caching will be disabled.")
            self.redis_client = None

    def set(self, data: str, request: PriceTicketRequest, ttl: int) -> None:
        if not self.redis_client:
            return
            
        try:
            key = self.construct_key(request)
            logger.info(f"Caching data for key: {key} with TTL: {ttl / 60:.1f} minutes")
            self.redis_client.set(name=key, value=data, ex=ttl)
        except Exception as e:
            logger.warning(f"Failed to cache data: {e}")

    def get(self, request: PriceTicketRequest) -> str:
        if not self.redis_client:
            return None
            
        try:
            key = self.construct_key(request)
            response = self.redis_client.get(key)

            if response:
                logger.info(f"Cache hit for key: {key}")
                return response
            return None
        except Exception as e:
            logger.warning(f"Failed to get cached data: {e}")
            return None

    def construct_key(self, request: PriceTicketRequest) -> str:
        return f"{request.api_provider.value}:{request.crypto_id}:{request.interval}"
