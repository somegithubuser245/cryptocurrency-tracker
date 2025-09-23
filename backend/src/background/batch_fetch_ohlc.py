import asyncio
import json
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
from services.data_gather import DataManagerDependency
from services.db_session import DBSessionDep
from utils.dependencies.dependencies import CryptoFetcherDependency, RedisClientDependency

logger = logging.getLogger(__name__)
batch_settings = CryptoBatchSettings()


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
            threshold: int | None
        ) -> list[CryptoPair]:
        """
        Get all arbitrable pair objects

        Specify the threshold to be applied.
        I.e. min. amount of exchanges, which support this pair
        """
        # state management!
        # how do i know if the pairs have been initted already?
        # TODO: create a master state machine for general init statuses
        # e.g. initted all pairs, initted all exchange names, etc.

        threshold = threshold or batch_settings.DEFAULT_THRESHOLD

        # get pairs data with threshold applied
        all_ids = get_arbitrable_with_threshold(threshold=threshold, session=db)
        crypto_pairs_tuples = get_params_for_crypto_dto(ids_list=all_ids, session=db)

        return [ CryptoPair(
            crypto_id=crypto_id,
            crypto_name=crypto_name,
            supported_exchange=supported_exchange
        ) for crypto_id, crypto_name, supported_exchange
        in crypto_pairs_tuples ]


    async def download_all_ohlc(
        self,
        db: DBSessionDep,
        threshold: int | None = None
    ) -> None:
        """
        Download and save all ohcl in Redis

        All in this case means
        all arbitrable pairs with predefined threshold
        """
        crypto_dto_list = self.create_arb_pairs_objects(db=db, threshold=threshold)
        dtos_length = len(crypto_dto_list)

        for i in range(0, dtos_length, self.CHUNK_SIZE):
            chunk_end = min(i + self.CHUNK_SIZE, dtos_length)
            dto_chunk = crypto_dto_list[i:chunk_end]

            tasks = [dto.get_ohlc(self.external_api_caller) for dto in dto_chunk]
            # asyncio.gather returns the list saving the initial sequence
            ordered_ohlc = await asyncio.gather(*tasks)

            for dto, ohlc in zip(dto_chunk, ordered_ohlc, strict=True):
                self.redis_client.set(
                    key=str(dto),
                    data=json.dumps(ohlc),
                    ttl=batch_settings.DEFAULT_OHLC_TTL
                )

            await asyncio.sleep(batch_settings.DEFAULT_SLEEP_TIME)


async def get_batch_fetcher(
    redis_client: RedisClientDependency,
    data_manager: DataManagerDependency,
    external_api_caller: CryptoFetcherDependency,
) -> BatchFetcher:
    return BatchFetcher(
        data_manager=data_manager,
        redis_client=redis_client,
        external_api_caller=external_api_caller,
        chunk_size=batch_settings.DEFAULT_CHUNK_SIZE,
    )


BatchFetcherDependency = Annotated[BatchFetcher, Depends(get_batch_fetcher)]
