import ccxt

from app.models.schemas import PriceTicketRequest


class CryptoFetcher:
    """This is basically a reqest wrapper
    It just adds some binance API related PATHs
    and makes some additional checks
    """

    def __init__(self) -> None:
        pass

    def get_ohlc(self, request: PriceTicketRequest) -> list[list[float]]:
        exchange = self.get_exchange(request.api_provider)
        return exchange.fetch_ohlcv(
            request.crypto_id.replace("-", "/"),
            request.interval,
        )

    def get_exchange(self, exchange_name: str) -> ccxt.Exchange:
        return getattr(ccxt, exchange_name)()
