import asyncio
from config.config import Exchange
from routes.models.schemas import PriceTicker
from services.data_gather import DataManager
from services.spread_calculator import SpreadCalculator


async def get_them_pairs(
        data_manager: DataManager,
        spread_caclulator: SpreadCalculator
) -> None:
    arbitrable_pairs_with_exchanges = await data_manager.get_arbitrable_pairs()
    spreads = {}
    
    for crypto_id, supported_exchanges in arbitrable_pairs_with_exchanges.items():
        tickers = PriceTicker(
            crypto_id=crypto_id,
            api_provider=supported_exchanges[0],
            inteval="4h"
        ).many_exchanges_generator(supported_exchanges)

        raw_timeseries = await data_manager.get_ohlc_data_cached(tickers)
        
        calculated_spread = await spread_caclulator.create(
            pair=tickers[0],
            all_timeseries=raw_timeseries,
            exchange_names=supported_exchanges
        )

        spreads[crypto_id] = calculated_spread.get_max_spread()

    return spreads