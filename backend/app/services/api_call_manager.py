from app.models.schemas import CompareRequest, KlinesRequest
from app.services.timeframes_equalizer import Equalizer

from .caching import Cacher
from .external_api_caller import CryptoFetcher


class ApiCallManager:
    """Main class that handles calls from FastAPI"""

    def __init__(self) -> None:
        self.data_fetcher = CryptoFetcher()
        self.equalizer = Equalizer()
        self.redis_cacher = Cacher()

    def get_timeframe_aligned(self, request: CompareRequest) -> dict[str, dict[str, float | int]]:
        requests = [
            KlinesRequest(
                crypto_id=request.crypto_id,
                interval=request.interval,
                api_provider=request.exchange1,
            ),
            KlinesRequest(
                crypto_id=request.crypto_id,
                interval=request.interval,
                api_provider=request.exchange2,
            ),
        ]
        data_sets_raw = [self.data_fetcher.get_response(value) for value in requests]
        data_set1, data_set2 = self.equalizer.equalize_timeframes(
            data_sets_raw[0], data_sets_raw[1]
        )

        return {request.exchange1.value: data_set1, request.exchange2.value: data_set2}
