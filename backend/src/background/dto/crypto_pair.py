from utils.dependencies.dependencies import CryptoFetcherDependency


class CryptoPair:
    def __init__(
        self,
        *,
        crypto_id_exchange_unique: int,
        crypto_name: str,
        supported_exchange: str,
        interval: str,
    ) -> None:
        self.ce_id = crypto_id_exchange_unique
        self.crypto_name = crypto_name
        self.supported_exchange = supported_exchange
        self.interval = interval

    async def get_ohlc(self, crypto_fetcher: CryptoFetcherDependency) -> list[list[float]] | None:
        """
        Do some magic by passing in an external api caller

        Which will fetch the OHLC with the current class parameters
        """
        return await crypto_fetcher.get_ohlc_parameterised(
            crypto_name=self.crypto_name,
            exchange_name=self.supported_exchange,
            interval=self.interval,
        )

    def __repr__(self) -> str:
        return f"OHLC:{self.ce_id}"
