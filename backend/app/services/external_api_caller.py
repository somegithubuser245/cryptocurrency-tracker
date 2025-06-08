from datetime import datetime, timezone
import json
import ccxt

from app.models.schemas import KlinesRequest


class CryptoFetcher:
    """This is basically a reqest wrapper
    It just adds some binance API related PATHs
    and makes some additional checks
    """
    def __init__(self) -> None:
        pass

    async def get_response(self, request: KlinesRequest):
        exchange = self.get_exchange(request.api_provider)
        print(exchange)
        current_day = datetime.now()
        day_before = datetime(
            current_day.year,
            current_day.month,
            current_day.day - 1,
            current_day.hour,
            current_day.minute,
            current_day.second,
            current_day.microsecond,
            timezone.utc()
        )
        ohlc_data = exchange.fetch_ohlcv(
            request.crypto_id.replace("-", "/"), 
            request.interval,
            int(day_before.timestamp() * 1000)
            )
        print(ohlc_data)
        return json.dumps(ohlc_data)
        

    def get_exchange(self, exchange_name: str) -> ccxt.Exchange:
        return getattr(ccxt, exchange_name)()