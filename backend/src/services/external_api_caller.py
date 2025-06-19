import asyncio

import ccxt.async_support as ccxt
from routes.models.schemas import PriceTicketRequest


class CryptoFetcher:
    """
    CCXT wrapper with internal functions
    """

    def __init__(self) -> None:
        self._exchanges: dict[str, ccxt.Exchange] = {}

    async def get_ohlc(self, request: PriceTicketRequest) -> list[list[float]]:
        exchange = self.get_exchange(request.api_provider.value)
        return await exchange.fetch_ohlcv(
            request.crypto_id.replace("-", "/"),
            request.interval,
        )

    def get_exchange(self, exchange: str) -> ccxt.Exchange:
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
