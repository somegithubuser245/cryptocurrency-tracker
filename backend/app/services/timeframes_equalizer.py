import numpy as np
import pandas as pd


class Equalizer:
    def __init__(self) -> None:
        self.cnames = ["time", "open", "high", "low", "close", "volume"]

    def equalize_timeframes(
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

    def get_2d_names(self, cnames: list[str], appendix: str) -> list[str]:
        return [cname + f"_{appendix}" for cname in cnames if cname != "volume"]
