import pandas as pd

class Spread:
    def __init__(
        self,
        raw_frames: list[pd.DataFrame],
        exchange_names: list[str],
        pair_name: str
    ) -> None:
        """
        Based on raw frames for single token, calculate spread
        Then initilize DataFrame attribute
        """
        self.pair_name = pair_name
        spreads_series = (
            pd.concat(raw_frames, keys=exchange_names)
            .unstack(level=0)
            # main function for calculation
            ["close"].apply(self._calculate_max_spread_per_row, axis=1)
        )
        print(spreads_series)

        self.spreads_df = pd.DataFrame.from_records(
            data=spreads_series,
            columns=["spread", "spread_percent", "high_exchange", "low_exchange"],
            index=spreads_series.index
        )

    def _calculate_max_spread_per_row(self, x: pd.Series):
        exchange_names = x.index.to_list()
        name1 = exchange_names[0]
        max_exchange_name, min_exchange_mane = name1, name1
        
        entry1 = x.iloc[0]
        max, min = entry1, entry1
        
        for i in range(1, len(x)):
            price_entry = x.iloc[i]
            if price_entry < min:
                min = price_entry
                min_exchange_mane = exchange_names[i]

            if price_entry > max:
                max = price_entry
                max_exchange_name = exchange_names[i]
    
        spread = max - min
        spread_percent = spread / ((max + min) / 2) * 100
        return spread, spread_percent, max_exchange_name, min_exchange_mane
    
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

    