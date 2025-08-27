from config.config import Exchange
from routes.models.schemas import PriceTicker


def generate_price_tickers(crypto_id: str, interval: str, exchanges: list[Exchange]):
    return [PriceTicker(
        crypto_id=crypto_id,
        interval=interval,
        exchange=exchange
    ) for exchange in exchanges]