import asyncio
import logging

import ccxt.async_support as ccxt
from routes.models.schemas import PriceTicker

logger = logging.getLogger(__name__)


class CryptoFetcher:
    """
    CCXT wrapper with internal functions
    """

    def __init__(self) -> None:
        self._exchanges: dict[str, ccxt.Exchange] = {}

    async def get_ohlc_with_request(self, request: PriceTicker) -> list[list[float]]:
        return self.get_ohlc_parameterised(
            crypto_name=request.crypto_name.replace("-", "/"),
            exchange_name=request.exchange_name,
            interval=request.interval
        )

    async def get_ohlc_parameterised(
        self,
        *,
        crypto_name: str,
        exchange_name: str,
        interval: str,
    ) -> list[list[float]]:
        exchange = self._get_saved_exchange(exchange_name)

        try:
            return await exchange.fetch_ohlcv(
                crypto_name,
                interval,
            )
        except ccxt.BaseError as e:
            logger.error(
                f"""
                Something went wrong when fetching ohlc for {crypto_name}
                with {exchange_name}
                Error: {str(e)}
                """
            )
            return None

    async def get_exchanges_with_markets(self, exchanges: list[str]) -> list[ccxt.Exchange]:
        """
        Get exchanges with markets loaded in async
        """
        exchanges_loaded = [self._get_saved_exchange(exchange) for exchange in exchanges]

        # load markets to be able to access .symbols of each exchange
        await asyncio.gather(*[exchange.load_markets() for exchange in exchanges_loaded])

        return exchanges_loaded

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
        logger.info("ON SHUTDOWN LIFESPAN CALLED!")

        await asyncio.gather(*tasks)
