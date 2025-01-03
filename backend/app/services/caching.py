import redis
import json
from app.models.schemas import PriceRequest
from app.config.config import settings
from app.config.binance_config import binance_settings

class Cacher():
    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST, 
            port=settings.REDIS_PORT, 
            db=settings.REDIS_DB)

    def set(self, data, request: PriceRequest):
        key = self.construct_key(request)
        json_data = json.dumps(data)
        ttl = binance_settings.CACHE_TTL_CONFIG[request.interval]
        self.redis_client.set(name=key, value=json_data, ex=ttl)

    def get(self, request: PriceRequest):
        key = self.construct_key(request)
        response = self.redis_client.get(key)

        if response: return json.loads(response)
        return None

    def construct_key(self, reqest: PriceRequest) -> str:
        return f"{reqest.chart_type}:{reqest.crypto_id}:{reqest.interval}"

