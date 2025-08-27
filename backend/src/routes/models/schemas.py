from config.config import SUPPORTED_EXCHANGES, SUPPORTED_PAIRS, TIME_RANGES, Exchange
from pydantic import BaseModel

config_types: dict[str, dict] = {
    "timeranges": TIME_RANGES,
    "pairs": SUPPORTED_PAIRS,
    "exchanges": SUPPORTED_EXCHANGES,
}

class RedisCacheble(BaseModel):
    def construct_key(self) -> str:
        raise NotImplementedError
    
    def separate_strings_with_colons(self, *parameters: list[str]) -> str:
        key = ""
        for index, parameter in enumerate(parameters):
            key += f"{parameter}:" if index < len(parameters) - 1 else parameter
        return key


class CompareRequest(RedisCacheble):
    exchange1: Exchange
    exchange2: Exchange
    crypto_id: str
    interval: str = "1h"

    def construct_key(self):
        return super().separate_strings_with_colons(
            *self.model_dump().values()
        )


class PriceTicker(RedisCacheble):
    crypto_id: str
    interval: str = "1h"
    api_provider: Exchange
    supported_exchanges: list[Exchange] | None = None

    def construct_key(self):
        return f"{self.api_provider}:{self.crypto_id}:{self.interval}"
    
    def many_exchanges_generator(self, exchange_names: list[Exchange]) -> list["PriceTicker"]:
        return [
        PriceTicker(
            crypto_id=self.crypto_id,
            interval=self.interval,
            api_provider=exchange_name
        ) for exchange_name in exchange_names ]
