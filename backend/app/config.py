import logging
import enum

logger = logging.getLogger("uvicorn.error")
COINGECKO_API_URL = "https://api.coingecko.com/api/v3"
BINANCE_API_URL = "https://data-api.binance.vision/api/v3" # market-data only API

BINANCE_SUPPORTED_COINS = {
    'bitcoin': 'BTCUSDT',
    'ethereum': 'ETHUSDT',
    'dogecoin': 'DOGEUSDT',
    'solana': 'SOLUSDT'
}

