from pydantic import BaseModel


class RedisCacheble(BaseModel):
    def construct_key(self) -> str:
        raise NotImplementedError

    def separate_strings_with_colons(self, *parameters: list[str]) -> str:
        key = ""
        for index, parameter in enumerate(parameters):
            key += f"{parameter}:" if index < len(parameters) - 1 else parameter
        return key


class PriceTicker(RedisCacheble):
    crypto_id: int | None = None
    crypto_name: str
    exchange_name: str
    interval: str = "1h"
