import ccxt.async_support as ccxt
import numpy as np
import pandas as pd


class Converter:
    def __init__(self) -> None:
        pass

    def get_list_like(self, exchanges: list[ccxt.Exchange]) -> dict[str, list[str]]:
        """
        Generate a dict for arbitrable pairs

        Returns
        ----
        dictionary containing Pair as a key and list of Exchanges as a value

        Example:
        ```
        {
        "BTC-USDT": ["Binance", "okx", "mexc", "bingx"],
        "DOGE-USDT": ["bingx", "okx"],
        ...
        }
        ```
        """
        converted = self._convert_and_filter(exchanges)
        converted.fillna(False, inplace=True)
        supported_exchanges_list_like = converted.apply(
            # x[x] is equivalent to "select all x, where x is True"
            lambda x: x[x].index.tolist(),
            axis=1,
        )
        # convert to desired format
        # it may be not the best format to pipe further into data analysis functions
        return supported_exchanges_list_like.to_dict()

    def _convert_and_filter(
        self, exchanges: list[ccxt.Exchange], min_exchanges_available: int = 2
    ) -> pd.DataFrame:
        symbols_frames_raw = [
            pd.DataFrame({exchange.id: np.True_}, index=exchange.symbols, dtype=np.bool)
            for exchange in exchanges
        ]

        left_merge_frame = symbols_frames_raw[0]

        # TODO concat should be a better way...
        for right_merge_frame in symbols_frames_raw[1:]:
            left_merge_frame = left_merge_frame.merge(
                right_merge_frame, how="outer", left_index=True, right_index=True
            )

        # drop based on min exchanges available parameter
        return left_merge_frame.dropna(thresh=min_exchanges_available)
