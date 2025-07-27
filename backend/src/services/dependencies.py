from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from data_handling.exchanges_symbols_converter import Converter
from data_handling.timeframes_equalizer import Equalizer
from services.api_call_manager import ApiCallManager
from services.caching import Cacher
from services.data_gather import DataManager
from services.external_api_caller import CryptoFetcher

@lru_cache()
def get_cacher() -> Cacher:
    return Cacher()

@lru_cache()
def get_crypto_fetcher() -> CryptoFetcher:
    return CryptoFetcher()

@lru_cache()
def get_converter(fetcher: CryptoFetcher = Depends(get_crypto_fetcher)) -> Converter:
    # Note: min_exchanges_available is now configurable
    return Converter(fetcher=fetcher)

@lru_cache()
def get_equalizer() -> Equalizer:
    return Equalizer()

@lru_cache()
def get_data_manager(
    fetcher: CryptoFetcher = Depends(get_crypto_fetcher),
    cacher: Cacher = Depends(get_cacher),
) -> DataManager:
    return DataManager(fetcher=fetcher, cacher=cacher)


@lru_cache()
def get_api_call_manager(
    fetcher: CryptoFetcher = Depends(get_crypto_fetcher),
    data_manager: DataManager = Depends(get_data_manager),
    converter: Converter = Depends(get_converter),
    equalizer: Equalizer = Depends(get_equalizer),
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