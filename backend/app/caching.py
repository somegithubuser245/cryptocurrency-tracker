import redis
import json

class Cacher():
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

    def set(self, data, crypto_id: str, days: str, type: str = "ohlc"):
        key = self.construct_key(crypto_id, days, type)
        json_data = json.dumps(data)
        self.redis_client.set(key, json_data)

    def get(self, crypto_id: str, days: str, type: str = "ohlc"):
        key = self.construct_key(crypto_id, days, type)
        response = self.redis_client.get(key)
        if response:
            return json.loads(response)
        return None

    def construct_key(self, crypto_id: str, days: str, type: str) -> str:
        return f"{type}:{crypto_id}:{days}"

