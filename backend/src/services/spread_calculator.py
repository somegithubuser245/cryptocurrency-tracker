from typing import Annotated

from data_manipulation.spread_object import Spread
from data_manipulation.timeframes_equalizer import TimeframesSyncDependency
from fastapi import Depends
from routes.models.schemas import PriceTicker


class SpreadCalculator:
    def __init__(self, timeframe_synchronizer: TimeframesSyncDependency) -> None:
        self.synchronizer = timeframe_synchronizer

    async def create(
        self, pair: PriceTicker, all_timeseries: list, exchange_names: list[str]
    ) -> Spread:
        """
        Creates a Spread Object based on the supported exchanges for the specified crypto pair
        """
        aligned = self.synchronizer.sync_many(all_timeseries)

        return Spread(pair_name=pair.crypto_id, raw_frames=aligned, exchange_names=exchange_names)


SpreadCalculatorDependency = Annotated[SpreadCalculator, Depends()]
