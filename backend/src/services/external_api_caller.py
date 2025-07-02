import asyncio

import ccxt.async_support as ccxt
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

        # TODO: use pandas for quicker data preprocessing
        all_symbols = [symbol for exchange in exchanges for symbol in exchange.symbols]
        unique_symbols = list(set(all_symbols))
        arbitrable_symbols = sorted(
            [symbol for symbol in unique_symbols if all_symbols.count(symbol) > 1]
        )

        pairs_exchanges_dict: dict[str, list[str]] = {}
        for symbol in arbitrable_symbols:
            for exchange in exchanges:
                exchange_name = exchange.id
                if symbol not in exchange.symbols:
                    continue
                if pairs_exchanges_dict.get(symbol):
                    pairs_exchanges_dict[symbol].append(exchange_name)
                else:
                    pairs_exchanges_dict[symbol] = [exchange_name]

        return pairs_exchanges_dict

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
