import logging
from typing import Annotated

import pandas as pd
from fastapi import Depends

logger = logging.getLogger(__name__)


class TimeframeSynchronizer:
    def __init__(self) -> None:
        self._cnames = ["time", "open", "high", "low", "close", "volume"]

    def sync_two(
        self,
        klines_data1: list[list[float]],
        klines_data2: list[list[float]],
        columns_to_drop: list[str] | None = None,
    ) -> tuple[list[dict], list[dict]]:
        klines_df1 = pd.DataFrame(klines_data1, columns=self.cnames).set_index(self.cnames[0])
        klines_df2 = pd.DataFrame(klines_data2, columns=self.cnames).set_index(self.cnames[0])

        # Remove volume column if not needed
        if columns_to_drop:
            klines_df1.drop(columns_to_drop, axis=1, inplace=True)
            klines_df2.drop(columns_to_drop, axis=1, inplace=True)

        # Align the dataframes to have matching timestamps
        sorted1, sorted2 = klines_df1.align(klines_df2, join="inner", axis=0)

        # Convert to list of dictionaries with timestamp included
        result1 = sorted1.reset_index().assign(time=lambda x: x["time"] / 1000).to_dict("records")
        result2 = sorted2.reset_index().assign(time=lambda x: x["time"] / 1000).to_dict("records")

        return (result1, result2)

    def sync_many(self, ohlc_data_entries: list[list[list[float]]]) -> list[pd.DataFrame]:
        dataframes_raw: list[pd.DataFrame] = []
        for ohlc_entry in ohlc_data_entries:
            if len(ohlc_entry[0]) != len(self._cnames):
                logger.info("OHLC CORRUPTED! SKIPPING")
                continue

            df = pd.DataFrame(ohlc_entry, columns=self._cnames).set_index(self._cnames[0])
            df.index = pd.to_datetime(df.index, unit="ms", origin="unix", utc=True)
            dataframes_raw.append(df)

        common_index = dataframes_raw[0].index
        for df in dataframes_raw[1:]:
            common_index = df.index.intersection(common_index)

        return [df.loc[common_index] for df in dataframes_raw]

TimeframesSyncDependency = Annotated[TimeframeSynchronizer, Depends()]