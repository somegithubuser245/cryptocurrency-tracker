import asyncio

import ccxt.async_support as ccxt
from models.schemas import PriceTicketRequest


class CryptoFetcher:
    """This is basically a reqest wrapper
    It just adds some binance API related PATHs
    and makes some additional checks
    """

    def __init__(self) -> None:
        self._exchanges: dict[str, ccxt.Exchange] = {}

    async def get_ohlc(self, request: PriceTicketRequest) -> list[list[float]]:
        exchange = self.get_exchange(request.api_provider)
        return await exchange.fetch_ohlcv(
            request.crypto_id.replace("-", "/"),
            request.interval,
        )

    def get_exchange(self, exchange: str) -> ccxt.Exchange:
        if exchange not in self._exchanges:
            self._exchanges[exchange] = self.get_ccxt_exchange(exchange)
        return self._exchanges.get(exchange)

    def get_ccxt_exchange(self, exchange_name: str) -> ccxt.Exchange:
        return getattr(ccxt, exchange_name)()

    async def close_all(self) -> None:
        if not self._exchanges:
            return

        tasks = []
        for exchange in self._exchanges.values():
            tasks.append(exchange.close())

        await asyncio.gather(*tasks)

    async def __aenter__(self) -> "CryptoFetcher":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> "CryptoFetcher":  # noqa: ANN001
        await self.close_all()
