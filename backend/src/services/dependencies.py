from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from data_handling.exchanges_symbols_converter import Converter
from data_handling.timeframes_equalizer import TimeframeSynchronizer
from services.api_call_manager import ApiCallManager
from services.caching import Cacher
from services.data_gather import DataManager
from services.external_api_caller import CryptoFetcher
from services.spread_calculator import SpreadCalculator

@lru_cache()
def get_cacher() -> Cacher:
    return Cacher()

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
    cacher: Cacher = Depends(get_cacher),
    converter: Converter = Depends(get_converter)
) -> DataManager:
    return DataManager(fetcher=fetcher, redis_cacher=cacher, converter=converter)

@lru_cache()
def get_spreads_calculator(
    data_manager: DataManager = Depends(get_data_manager),
    equalizer: TimeframeSynchronizer = Depends(get_equalizer)
) -> SpreadCalculator:
    return SpreadCalculator(data_manager=data_manager, timeframe_synchronizer=equalizer)


@lru_cache()
def get_api_call_manager(
    fetcher: CryptoFetcher = Depends(get_crypto_fetcher),
    data_manager: DataManager = Depends(get_data_manager),
    converter: Converter = Depends(get_converter),
    equalizer: TimeframeSynchronizer = Depends(get_equalizer),
) -> ApiCallManager:
    """
    Provides an ApiCallManager instance with all its dependencies injected.
    lru_cache ensures a single instance is created and reused across requests.
    """
    return ApiCallManager(
        fetcher=fetcher,
        data_manager=data_manager,
        converter=converter,
        equalizer=equalizer,
    )

call_manager_dependency = Annotated[ApiCallManager, Depends(get_api_call_manager)]
spreads_calculator_dependency = Annotated[SpreadCalculator, Depends(get_spreads_calculator)]