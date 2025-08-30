
from data_handling.spread_object import Spread
from data_handling.timeframes_equalizer import TimeframeSynchronizer
from routes.models.schemas import PriceTicker


class SpreadCalculator:
    def __init__(
            self,
            timeframe_synchronizer: TimeframeSynchronizer
    ) -> None:
        self.synchronizer = timeframe_synchronizer

    async def create(
            self,
            pair: PriceTicker,
            all_timeseries: list,
            exchange_names: list[str]
            ) -> Spread:
        """
        Creates a Spread Object based on the supported exchanges for the specified crypto pair
        """
        aligned = self.synchronizer.sync_many(all_timeseries)

        return Spread(
            pair_name=pair.crypto_id,
            raw_frames=aligned,
            exchange_names=exchange_names
        )



