import asyncio
import json
import logging
from typing import Annotated

from background.celery.celery_spreads import run_chunk_compute
from background.db.batch_status import init_batch_status, update_batch_status_cached
from background.db.db_pairs import (
    get_arbitrable_rows,
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
        chunk_size: int,
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
        arbitrable_crypto_ids: list[int],
        interval: str,
        db: DBSessionDep,
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
        crypto_pairs_tuples = get_params_for_crypto_dto(ids_list=arbitrable_crypto_ids, session=db)

        return [
            CryptoPair(
                crypto_id_exchange_unique=crypto_id,
                crypto_name=crypto_name,
                supported_exchange=supported_exchange,
                interval=interval,
            )
            for crypto_id, crypto_name, supported_exchange in crypto_pairs_tuples
        ]

    async def download_all_ohlc(
        self, db: DBSessionDep, threshold: int | None = None, interval: str | None = None
    ) -> None:
        """
        Download and save all ohcl in Redis

        All in this case means
        all arbitrable pairs with predefined threshold
        """
        threshold = threshold or batch_settings.DEFAULT_THRESHOLD
        interval = interval or batch_settings.DEFAULT_INTERVAL

        # get pairs data with threshold applied
        raw_rows = get_arbitrable_rows(threshold=threshold, session=db)
        crypto_ids = [row.crypto_id for row in raw_rows]
        ids_with_exchange = [row.id for row in raw_rows]

        # initialize batch status table
        init_batch_status(
            session=db,
            ids_by_exchange=ids_with_exchange,
            crypto_ids=crypto_ids,
            interval=interval,
        )

        crypto_dto_list: list[CryptoPair] = self.create_arb_pairs_objects(
            db=db, arbitrable_crypto_ids=ids_with_exchange, interval=interval
        )

        for i in range(0, len(crypto_dto_list), self.CHUNK_SIZE):
            chunk_end = min(i + self.CHUNK_SIZE, len(crypto_dto_list))
            dto_chunk = crypto_dto_list[i:chunk_end]
            await self.process_chunk(dto_chunk=dto_chunk, db=db)

    async def process_chunk(
        self,
        dto_chunk: list[CryptoPair],
        db: DBSessionDep,
    ) -> None:
        tasks = [dto.get_ohlc(self.external_api_caller) for dto in dto_chunk]

        # asyncio.gather returns the list saving the initial sequence
        ordered_ohlc = await asyncio.gather(*tasks)

        cached_ce_ids = []
        for dto, ohlc in zip(dto_chunk, ordered_ohlc, strict=True):
            # skip corrupted / unfilled ohlc
            # won't flag as cached in status table
            if not ohlc:
                continue

            self.redis_client.set(
                key=str(dto), data=json.dumps(ohlc), ttl=batch_settings.DEFAULT_OHLC_TTL
            )
            cached_ce_ids.append(dto.ce_id)

        update_batch_status_cached(
            session=db,
            ce_ids=cached_ce_ids,
        )
        run_chunk_compute(ce_ids=cached_ce_ids)

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
