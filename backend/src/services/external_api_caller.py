import asyncio

import ccxt.async_support as ccxt
import pandas as pd
import numpy as np
from config.config import SUPPORTED_EXCHANGES
from routes.models.schemas import PriceTicketRequest


class CryptoFetcher:
    """
    CCXT wrapper with internal functions
    """

    def __init__(self) -> None:
        self._exchanges: dict[str, ccxt.Exchange] = {}

    async def get_ohlc(self, request: PriceTicketRequest) -> list[list[float]]:
        exchange = self.get_saved_exchange(request.api_provider.value)
        return await exchange.fetch_ohlcv(
            request.crypto_id.replace("-", "/"),
            request.interval,
        )

    async def get_arbitrable_pairs(self) -> dict[str, list[str]]:
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
        exchanges = [self.get_saved_exchange(exchange) for exchange in SUPPORTED_EXCHANGES.values()]

        # load markets to be able to access .symbols of each exchange
        await asyncio.gather(*[exchange.load_markets() for exchange in exchanges])

        symbols_frames_raw = [
            pd.DataFrame({exchange.id: exchange.symbols}) for exchange in exchanges
        ]

        left_merge_frame = symbols_frames_raw[0]

        for right_merge_frame in symbols_frames_raw[1:]:
            left_name = left_merge_frame.columns[-1]
            right_name = right_merge_frame.columns[0]

            left_merge_frame = left_merge_frame.merge(
                right_merge_frame,
                how="outer",
                left_on=left_name,
                right_on=right_name,
            )

            print(left_merge_frame.dropna().head())

        # drop only if found on single exchange
        threshold = 2
        left_merge_frame.dropna(thresh=threshold, inplace=True)

        print(left_merge_frame.transpose())
        return left_merge_frame.to_dict(
            orient="index"
        )

    def get_saved_exchange(self, exchange: str) -> ccxt.Exchange:
        if exchange not in self._exchanges:
            self._exchanges[exchange] = self.get_ccxt_exchange(exchange)
        return self._exchanges[exchange]

    def get_ccxt_exchange(self, exchange_name: str) -> ccxt.Exchange:
        return getattr(ccxt, exchange_name)()

    async def close_all(self) -> None:
        """Close all exchange connections after completing async call"""
        if not self._exchanges:
            return

        tasks = []
        for exchange in self._exchanges.values():
            tasks.append(exchange.close())

        await asyncio.gather(*tasks)
