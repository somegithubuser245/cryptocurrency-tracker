import logging

import pandas as pd

# derived from DB Model names
DEFAULT_COLUMN_NAMES = ["spread", "spread_percent", "high_exchange_id", "low_exchange_id"]
DEFAULT_COLUMNS_TO_KEEP = ["time", "spread_percent", "high_exchange_id", "low_exchange_id"]

logger = logging.getLogger(__name__)


class Spread:
    def __init__(
        self,
        raw_frames: list[pd.DataFrame],
        preferred_column_names: list[str] | None = DEFAULT_COLUMN_NAMES,
        exchange_names: list[str] | None = None,
        ce_ids: list[int] | None = None,
    ) -> None:
        """
        Based on raw frames for single token, calculate spread.
        Then initilize DataFrame attribute

        You can specify your own preferred column names.
        Defaults to DB Model of ComputedSpreadMax
        """
        if not ce_ids and not exchange_names:
            msg = "NO INDEX IDENTIFICATORS PROVIDED"
            logger.error(msg)
            raise ValueError(msg)

        self._cnames = preferred_column_names
        keys = ce_ids or exchange_names

        spreads_series = (
            pd.concat(raw_frames, keys=keys)
            .unstack(level=0)[
                # main function for calculation
                "close"
            ]
            .apply(self._calculate_max_spread_per_row, axis=1)
        )

        self.spreads_df = self._construct_frame_from_records(
            data=spreads_series, index=spreads_series.index
        )

    def _construct_frame_from_records(self, data: pd.Series, index: pd.Index) -> pd.DataFrame:
        return pd.DataFrame.from_records(data=data, columns=self._cnames, index=index)

    def _calculate_max_spread_per_row(self, x: pd.Series) -> tuple[int | str]:
        max, min = x.max(), x.min()
        max_exchange_name, min_exchange_name = x.idxmax(), x.idxmin()

        spread = max - min
        spread_percent = spread / ((max + min) / 2) * 100
        return spread, spread_percent, max_exchange_name, min_exchange_name

    # api-ready dicts
    def get_max_spread(self, columns_to_keep: list[str] = DEFAULT_COLUMNS_TO_KEEP) -> dict:
        """
        Get maximum spread found for the whole pair
        """
        # reset index
        # .loc returns a Series, which means that index won't be accessible
        # this is the only reason for conversion
        unindexed = self.spreads_df.reset_index()
        max_timestamp = unindexed["spread_percent"].idxmax()

        max_row = unindexed.loc[max_timestamp]
        return max_row[columns_to_keep].to_dict()

    def get_as_dict(self) -> dict:
        return self.spreads_df.to_dict(orient="index")
