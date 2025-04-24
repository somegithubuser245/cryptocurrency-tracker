from pydantic_settings import BaseSettings

# use this link for reference. it's binance api docs for market data
# https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints
BINANCE_API_URL: str = "https://data-api.binance.vision/api/v3"

SUPPORTED_PAIRS: dict = {
    'BTCUSDT': 'BTCUSDT',
    'ETHUSDT': 'ETHUSDT',
    'SOLUSDT': 'SOLUSDT',
    'ADAUSDT': 'ADAUSDT',
    'AVAXUSDT': 'AVAXUSDT',
    'DOTUSDT': 'DOTUSDT'
}

TIME_RANGES: dict = {
    "5m": "5m",
    "30m": "30m",
    "1H": "1h",
    "4H": "4h",
    "1D": "1d",
    "1W": "1w",
    "1M": "1M"
}