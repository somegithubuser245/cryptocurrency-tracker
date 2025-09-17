from functools import lru_cache
from typing import Annotated

from data_manipulation.exchanges_symbols_converter import Converter
from data_manipulation.timeframes_equalizer import TimeframeSynchronizer
from fastapi import Depends
from services.caching import RedisClient
from services.data_gather import DataManager
from services.external_api_caller import CryptoFetcher
from services.spread_calculator import SpreadCalculator


@lru_cache()
def get_cacher() -> RedisClient:
    return RedisClient()


@lru_cache()
def get_crypto_fetcher() -> CryptoFetcher:
    return CryptoFetcher()


@lru_cache()
def get_converter() -> Converter:
    return Converter()


@lru_cache()
def get_equalizer() -> TimeframeSynchronizer:
    return TimeframeSynchronizer()


@lru_cache()
def get_data_manager(
    fetcher: CryptoFetcher = Depends(get_crypto_fetcher),
    cacher: RedisClient = Depends(get_cacher),
    converter: Converter = Depends(get_converter),
) -> DataManager:
    return DataManager(fetcher=fetcher, redis_cacher=cacher, converter=converter)


@lru_cache()
def get_spreads_calculator(
    equalizer: TimeframeSynchronizer = Depends(get_equalizer),
) -> SpreadCalculator:
    return SpreadCalculator(timeframe_synchronizer=equalizer)


spreads_calculator_dependency = Annotated[SpreadCalculator, Depends(get_spreads_calculator)]
converter_dependency = Annotated[Converter, Depends(get_converter)]
RedisClientDependency = Annotated[RedisClient, Depends(get_cacher)]
DataManagerDependency = Annotated[DataManager, Depends(get_data_manager)]
CryptoFetcherDependency = Annotated[CryptoFetcher, Depends(get_crypto_fetcher)]
