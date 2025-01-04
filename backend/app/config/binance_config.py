from pydantic_settings import BaseSettings

# use this link for reference. it's binance api docs for market data
# https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints

class BinanceSettings(BaseSettings):
    # market-data only api endpoint
    BINANCE_API_URL: str = "https://data-api.binance.vision/api/v3"

    # used for redis ttl
    CACHE_TTL_CONFIG: dict = {
        "5m": 300,
        "30m": 1800,
        "1h": 3600,
        "4h": 14400,
        "1d": 86400,
        "1w": 604800,
        "1M": 604800,
    }

    # used for frontend
    SUPPORTED_PAIRS: dict = {
        'BTCUSDT': 'Bitcoin',
        'ETHUSDT': 'Ethereum',
        'SOLUSDT': 'Solana',
        'ADAUSDT': 'Cardano',
        'AVAXUSDT': 'Avalanche',
        'DOTUSDT': 'Polkadot'
    }

    # used for frontend
    TIME_RANGES: dict = {
        "5m": "5 minutes",
        "30m": "30 minutes",
        "1h": "Hourly",
        "4h": "4 Hours",
        "1d": "Daily",
        "1w": "Weekly",
        "1M": "Monthly"
    }

    DATA_TYPES: list = [
        'klines'
    ]

binance_settings = BinanceSettings()