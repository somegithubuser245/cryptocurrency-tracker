from config.config import CryptoBatchSettings
from utils.dependencies.dependencies import CryptoFetcherDependency


class CryptoPair:
    def __init__(
        self,
        *,
        crypto_id: int,
        crypto_name: str,
        supported_exchange: str,
    ) -> None:
        self.crypto_id = crypto_id
        self.crypto_name = crypto_name
        self.supported_exchange = supported_exchange
        self.interval = self._get_current_default_interval()

    def _get_current_default_interval(self) -> str:
        """
        Currently just returns the DEFAULT INTERVAL

        It's planned to receive it from DB with user-based
        default setting later
        """
        return CryptoBatchSettings().DEFAULT_INTERVAL

    async def get_ohlc(
        self,
        crypto_fetcher: CryptoFetcherDependency
    ) -> list[list[float]]:
        """
        Do some magic by passing in an external api caller

        Which will fetch the OHLC with the current class parameters
        """
        return await crypto_fetcher.get_ohlc_parameterised(
            crypto_name=self.crypto_name,
            exchange_name=self.supported_exchange,
            interval=self.interval
        )

    def __repr__(self) -> str:
        return f"OHLC:{self.crypto_id}:{self.supported_exchange}:{self.interval}"
