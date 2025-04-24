from .config import TIME_RANGES as TR

OKX_API_URL = "https://eea.okx.com"

SUPPORTED_PAIRS: dict = {
    'BTCUSDT': 'BTC-USDT',
    'ETHUSDT': 'ETH-USDT',
    'SOLUSDT': 'SOL-USDT',
    'ADAUSDT': 'ADA-USDT',
    'AVAXUSDT': 'AVAX-USDT',
    'DOTUSDT': 'DOT-USDT'
}

TIME_RANGES: dict = {
    "5m": "5m",
    "30m": "30m",
    "1H": "1H",
    "4H": "4H",
    "1D": "1D",
    "1W": "1W",
    "1M": "1M"
}

TIME_RANGES_TEST = {key: key for key in TR}

DATA_TYPES: list = [
    'klines'
]