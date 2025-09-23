import asyncio
import logging
from typing import Annotated

from background.db_pairs import (
    get_arbitrable_with_threshold,
    get_params_for_crypto_dto,
    insert_exchange_names,
    insert_or_update_pairs,
)
from background.dto.crypto_pair import CryptoPair
from config.config import SUPPORTED_EXCHANGES, CryptoBatchSettings
from fastapi import Depends
from routes.models.schemas import PriceTicker
from services.data_gather import DataManagerDependency
from services.db_session import DBSessionDep
from utils.dependencies.dependencies import CryptoFetcherDependency, RedisClientDependency

logger = logging.getLogger(__name__)


class BatchFetcher:
    def __init__(
        self,
        data_manager: DataManagerDependency,
        redis_client: RedisClientDependency,
        external_api_caller: CryptoFetcherDependency,
        chunk_size: int = 100,
    ) -> None:
        self.data_manager = data_manager
        self.redis_client = redis_client
        self.external_api_caller = external_api_caller

        self.CHUNK_SIZE = chunk_size

    async def init_pairs_db(self, db: DBSessionDep) -> None:
        exchanges_with_symbols = await self.external_api_caller.get_exchanges_with_markets(
            list(SUPPORTED_EXCHANGES.values())
        )
        for exchange in exchanges_with_symbols:
            exchange_name = exchange.id
            exchange_symbols = exchange.symbols
            insert_or_update_pairs(exchange.symbols, db)
            insert_exchange_names(exchange_name, exchange_symbols, db)

    def create_arb_pairs_objects(
            self,
            db: DBSessionDep,
            threshold: int = CryptoBatchSettings().DEFAULT_THRESHOLD
        ) -> list:
        """
        Get all arbitrable pair objects

        Specify the threshold to be applied.
        I.e. min. amount of exchanges, which support this pair
        """
        # state management!
        # how do i know if the pairs have been initted already?
        # TODO: create a master state machine for general init statuses
        # e.g. initted all pairs, initted all exchange names, etc.


        # get pairs data with threshold applied
        all_ids = get_arbitrable_with_threshold(threshold=threshold, session=db)
        crypto_pairs_tuples = get_params_for_crypto_dto(ids_list=all_ids, session=db)

        return [ CryptoPair(
            crypto_id=crypto_id,
            crypto_name=crypto_name,
            supported_exchange=supported_exchange
        ) for crypto_id, crypto_name, supported_exchange
        in crypto_pairs_tuples ]


    async def download_all_ohlc(self) -> None:
        pass


    def log_info(self, ch_start: int, ch_end: int, downloaded_ohlc: list[str]) -> None:
        msg = f"chunk start: {ch_start}, chunk_end: {ch_end}, downloaded_ohlc: {downloaded_ohlc}"
        logger.info(msg)


async def get_batch_fetcher(
    redis_client: RedisClientDependency,
    data_manager: DataManagerDependency,
    external_api_caller: CryptoFetcherDependency,
) -> BatchFetcher:
    return BatchFetcher(
        data_manager=data_manager,
        redis_client=redis_client,
        external_api_caller=external_api_caller,
        chunk_size=CryptoBatchSettings().DEFAULT_CHUNK_SIZE,
    )


BatchFetcherDependency = Annotated[BatchFetcher, Depends(get_batch_fetcher)]
