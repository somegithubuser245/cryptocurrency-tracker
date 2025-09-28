import logging
from typing import Annotated

import pandas as pd
from fastapi import Depends

logger = logging.getLogger(__name__)


class TimeframeSynchronizer:
    def __init__(self) -> None:
        self._cnames = ["time", "open", "high", "low", "close", "volume"]

    def sync_many(self, ohlc_data_entries: list[list[list[float]]]) -> list[pd.DataFrame]:
        dataframes_raw: list[pd.DataFrame] = []
        for ohlc_entry in ohlc_data_entries:
            if len(ohlc_entry[0]) != len(self._cnames):
                logger.error("OHLC CORRUPTED! SKIPPING")
                continue

            df = pd.DataFrame(ohlc_entry, columns=self._cnames).set_index(self._cnames[0])
            df.index = pd.to_datetime(df.index, unit="ms", origin="unix", utc=True)
            dataframes_raw.append(df)

        common_index = dataframes_raw[0].index
        for df in dataframes_raw[1:]:
            common_index = df.index.intersection(common_index)

        return [df.loc[common_index] for df in dataframes_raw]

TimeframesSyncDependency = Annotated[TimeframeSynchronizer, Depends()]