from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from services.caching import RedisClient
from services.external_api_caller import CryptoFetcher


@lru_cache()
def get_redis_client() -> RedisClient:
    return RedisClient()


@lru_cache()
def get_crypto_fetcher() -> CryptoFetcher:
    return CryptoFetcher()


# init heavy dependencies with lru cache singleton patterns
RedisClientDependency = Annotated[RedisClient, Depends(get_redis_client)]
CryptoFetcherDependency = Annotated[CryptoFetcher, Depends(get_crypto_fetcher)]