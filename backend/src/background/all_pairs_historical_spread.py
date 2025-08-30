from routes.models.schemas import PriceTicker
from services.data_gather import DataManager
from services.spread_calculator import SpreadCalculator


async def get_them_pairs(
        data_manager: DataManager,
        spread_caclulator: SpreadCalculator
) -> None:
    arbitrable_pairs_with_exchanges = await data_manager.get_arbitrable_pairs()

    all_tickers = []

    for crypto_id, supported_exchanges in arbitrable_pairs_with_exchanges.items():
        all_tickers.extend(PriceTicker.generate_with_many_exchanges(
            crypto_id=crypto_id,
            interval="4h",
            exchange_names=supported_exchanges
        ))

    all_timeseries_data = await data_manager.get_ohlc_data_cached(all_tickers)
    spreads = {}

    for crypto_id, supported_exchanges in arbitrable_pairs_with_exchanges.items():
        tickers = PriceTicker.generate_with_many_exchanges(
            crypto_id=crypto_id,
            interval="4h",
            exchange_names=supported_exchanges
        )
        try:
            raw_timeseries = [all_timeseries_data.get(ticker.construct_key()) for ticker in tickers]

            calculated_spread = await spread_caclulator.create(
                pair=tickers[0],
                all_timeseries=raw_timeseries,
                exchange_names=supported_exchanges
            )

            spreads[crypto_id] = calculated_spread.get_max_spread()
        except Exception as e:
            print(str(e))
            print(f"{crypto_id} Skipped!")

    return spreads
