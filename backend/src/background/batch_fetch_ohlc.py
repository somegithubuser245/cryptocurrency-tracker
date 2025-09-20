import asyncio
import logging
from typing import Annotated

from background.db_pairs import insert_exchange_names, insert_or_update_pairs
from config.config import SUPPORTED_EXCHANGES
from fastapi import Depends
from routes.models.schemas import PriceTicker
from services.caching import RedisClient
from services.data_gather import DataManager
from services.external_api_caller import CryptoFetcher
from utils.dependencies.dependencies import (
    CryptoFetcherDependency,
    DataManagerDependency,
    RedisClientDependency,
)

logger = logging.getLogger(__name__)


class BatchFetcher:
    def __init__(
        self,
        data_manager: DataManager,
        redis_client: RedisClient,
        external_api_caller: CryptoFetcher,
        chunk_size: int = 100,
    ) -> None:
        self.data_manager = data_manager
        self.redis_client = redis_client
        self.external_api_caller = external_api_caller

        self.CHUNK_SIZE = chunk_size

    async def init_pairs_db(self) -> None:
        exchanges_with_symbols = await self.external_api_caller.get_exchanges_with_markets(
            list(SUPPORTED_EXCHANGES.keys())
        )

        for exchange in exchanges_with_symbols:
            exchange_name = exchange.id
            exchange_symbols = exchange.symbols
            insert_or_update_pairs(exchange.symbols)
            insert_exchange_names(exchange_name, exchange_symbols)

    async def init_tickers_and_ids(self) -> tuple[list, str]:
        arbitrable_pairs_with_exchanges = await self.data_manager.get_arbitrable_pairs()
        insert_or_update_pairs(list(arbitrable_pairs_with_exchanges.keys()))
        crypto_ids = list(arbitrable_pairs_with_exchanges.keys())
        crypto_pairs_tickers = []

        for crypto_id, supported_exchanges in arbitrable_pairs_with_exchanges.items():
            crypto_pairs_tickers.extend(
                PriceTicker.generate_with_many_exchanges(
                    crypto_id=crypto_id, interval="4h", exchange_names=supported_exchanges
                )
            )

        return crypto_pairs_tickers, crypto_ids

    async def download_all_in_chunks(self) -> None:
        downloaded_ohlc_results = {}
        crypto_pairs_tickers, crypto_ids = await self.init_tickers_and_ids()

        crypto_pairs_len = len(crypto_pairs_tickers)

        for i in range(0, crypto_pairs_len, self.CHUNK_SIZE):
            chunk_end = min(i + self.CHUNK_SIZE, crypto_pairs_len)

            tickers_chunk = crypto_pairs_tickers[i:chunk_end]
            downloaded_ohlc = await self.data_manager.get_ohlc_data_cached(tickers_chunk)
            downloaded_ohlc_results.update(downloaded_ohlc)

            await asyncio.sleep(0.5)

        return downloaded_ohlc_results

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
        chunk_size=100,
    )


BatchFetcherDependency = Annotated[BatchFetcher, Depends(get_batch_fetcher)]
