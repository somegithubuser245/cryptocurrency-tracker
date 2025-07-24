import asyncio

import ccxt.async_support as ccxt
import numpy as np
import pandas as pd
from config.config import SUPPORTED_EXCHANGES
from routes.models.schemas import PriceTicketRequest


class CryptoFetcher:
    """
    CCXT wrapper with internal functions
    """

    def __init__(self) -> None:
        self._exchanges: dict[str, ccxt.Exchange] = {}

    async def get_ohlc(self, request: PriceTicketRequest) -> list[list[float]]:
        exchange = self._get_saved_exchange(request.api_provider.value)
        return await exchange.fetch_ohlcv(
            request.crypto_id.replace("-", "/"),
            request.interval,
        )

    async def get_exchanges(self) -> list[ccxt.Exchange]:
        """
        Generate a dict for arbitrable pairs

        Returns
        ----
        dictionary containing Pair as a key and list of Exchanges as a value

        Example:
        ```
        {
        "BTC-USDT": ["Binance", "okx", "mexc", "bingx"],
        "DOGE-USDT": ["bingx", "okx"],
        ...
        }
        ```
        """
        exchanges = [self._get_saved_exchange(exchange) for exchange in SUPPORTED_EXCHANGES.values()]

        # load markets to be able to access .symbols of each exchange
        await asyncio.gather(*[exchange.load_markets() for exchange in exchanges])

        return exchanges

    def _get_saved_exchange(self, exchange: str) -> ccxt.Exchange:
        if exchange not in self._exchanges:
            self._exchanges[exchange] = self._get_ccxt_exchange(exchange)
        return self._exchanges[exchange]

    def _get_ccxt_exchange(self, exchange_name: str) -> ccxt.Exchange:
        return getattr(ccxt, exchange_name)()

    async def close_all(self) -> None:
        """Close all exchange connections after completing async call"""
        if not self._exchanges:
            return

        tasks = []
        for exchange in self._exchanges.values():
            tasks.append(exchange.close())

        await asyncio.gather(*tasks)
