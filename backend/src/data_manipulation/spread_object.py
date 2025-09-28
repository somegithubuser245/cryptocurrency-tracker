import pandas as pd


class Spread:
    def __init__(
        self,
        raw_frames: list[pd.DataFrame],
        exchange_names: list[str] | None = None,
        ce_ids: list[int] | None = None
    ) -> None:
        """
        Based on raw frames for single token, calculate spread
        Then initilize DataFrame attribute
        """
        if not ce_ids and not exchange_names:
            raise ValueError("NO INDEX IDENTIFICATORS PROVIDED")

        keys = ce_ids or exchange_names
        spreads_series = (
            pd.concat(raw_frames, keys=keys)
            .unstack(level=0)
            # main function for calculation
            ["close"].apply(self._calculate_max_spread_per_row, axis=1)
        )

        self.spreads_df = pd.DataFrame.from_records(
            data=spreads_series,
            columns=["spread", "spread_percent", "high_exchange", "low_exchange"],
            index=spreads_series.index
        )

    def _calculate_max_spread_per_row(self, x: pd.Series) -> tuple[int | str]:
        max, min = x.max(), x.min()
        max_exchange_name, min_exchange_name = x.idxmax(), x.idxmin()

        spread = max - min
        spread_percent = spread / ((max + min) / 2) * 100
        return spread, spread_percent, max_exchange_name, min_exchange_name

    # api-ready dicts
    def get_max_spread(self) -> dict:
        # reset index
        # .loc returns a Series, which means that index won't be accessible
        # this is the only reason for conversion
        unindexed = self.spreads_df.reset_index()
        max_timestamp = unindexed["spread"].idxmax()

        return unindexed.loc[max_timestamp].to_dict()

    def get_as_dict(self) -> dict:
        return self.spreads_df.to_dict(orient="index")

