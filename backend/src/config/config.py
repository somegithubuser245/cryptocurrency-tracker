import logging
from enum import Enum

from pydantic_settings import BaseSettings


class ConfigSettings(BaseSettings):
    api_key: str = ""
    exchanges: list[str] = []
    
    # Redis configuration  
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    def __init__(self):
        super().__init__()


settings = ConfigSettings()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


class AppInfo:
    """
    Application-wide configuration
    """

    def __init__(self):
        self.name = "Crypto-Arbitrage-Backend"
        self.debug = False
        self.env = "dev"


APP_INFO = AppInfo()

# Exchange Configuration

logger = logging.getLogger(__name__)


class Exchange(str, Enum):
    BINANCE = "binance"
    COINBASE = "coinbase"
    KUCOIN = "kucoin"
    KRAKEN = "kraken"
    BITFINEX = "bitfinex"
    HUOBI = "huobi"
    OKX = "okx"
    GATE = "gate"
    BYBIT = "bybit"
    KUCION = "kucoin"


# Python 3.11 compatible StrEnum alternative
class TickerType(str, Enum):
    OHLC = "ohlc"
    CHART_LINE = "chart_line"


SUPPORTED_EXCHANGES: dict = {entry: entry.value for entry in Exchange}

# Cryptocurrency pairs configuration
SUPPORTED_PAIRS: dict = {
    "BTC/USD": "Bitcoin to USD",
    "ETH/USD": "Ethereum to USD", 
    "BTC/EUR": "Bitcoin to EUR",
    "ETH/EUR": "Ethereum to EUR",
    "ADA/USD": "Cardano to USD",
    "DOT/USD": "Polkadot to USD",
    "LINK/USD": "Chainlink to USD",
    "UNI/USD": "Uniswap to USD",
    "AAVE/USD": "Aave to USD",
    "SUSHI/USD": "SushiSwap to USD",
    "BTC/ETH": "Bitcoin to Ethereum",
    "ETH/BTC": "Ethereum to Bitcoin",
}

# Time ranges configuration
TIME_RANGES: dict = {
    "1m": "1 Minute",
    "5m": "5 Minutes", 
    "15m": "15 Minutes",
    "30m": "30 Minutes",
    "1h": "1 Hour",
    "4h": "4 Hours",
    "1d": "1 Day",
    "1w": "1 Week"
}
