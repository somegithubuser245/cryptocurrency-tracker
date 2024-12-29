import redis
import json
from models import PriceRequest

class Cacher():
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

    def set(self, data, request: PriceRequest):
        key = self.construct_key(request)
        json_data = json.dumps(data)
        self.redis_client.set(key, json_data)

    def get(self, request: PriceRequest):
        key = self.construct_key(request)
        response = self.redis_client.get(key)

        if response: return json.loads(response)
        return None

    def construct_key(self, reqest: PriceRequest) -> str:
        return f"{reqest.chart_type}:{reqest.crypto_id}:{reqest.days}"

