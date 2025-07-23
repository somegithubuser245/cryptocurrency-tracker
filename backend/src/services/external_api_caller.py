import asyncio
import time
import logging
from typing import Dict, List, Optional

import ccxt.async_support as ccxt
from ..config.config import SUPPORTED_EXCHANGES
from ..routes.models.schemas import PriceTicketRequest

logger = logging.getLogger(__name__)

class CryptoFetcher:
    """
    CCXT wrapper with aggressive caching and performance optimizations
    """

    def __init__(self) -> None:
        self._exchanges: dict[str, ccxt.Exchange] = {}
        
        # Aggressive caching for performance
        self._arbitrable_pairs_cache: Optional[Dict[str, List[str]]] = None
        self._arbitrable_pairs_cache_time: float = 0
        self._arbitrable_pairs_cache_ttl: float = 3600  # 1 hour cache
        
        # Markets cache per exchange  
        self._markets_cache: Dict[str, Dict] = {}
        self._markets_cache_time: Dict[str, float] = {}
        self._markets_cache_ttl: float = 1800  # 30 minutes cache
        
        # Loading state tracking to prevent duplicate API calls
        self._loading_arbitrable_pairs: bool = False
        self._loading_markets: Dict[str, bool] = {}

    async def get_ohlc(self, request: PriceTicketRequest) -> list[list[float]]:
        """Get OHLC data with caching"""
        exchange = self.get_saved_exchange(request.api_provider.value)
        
        try:
            # Ensure markets are loaded with caching
            await self._ensure_markets_loaded(exchange)
            
            symbol = request.crypto_id.replace("-", "/")
            return await exchange.fetch_ohlcv(symbol, request.interval)
        except Exception as e:
            logger.error(f"Error fetching OHLC data: {e}")
            # Return empty data instead of crashing
            return []

    async def get_arbitrable_pairs(self) -> dict[str, list[str]]:
        """
        Get arbitrable pairs with aggressive caching for performance
        
        This method is heavily optimized because it was the main performance bottleneck
        causing 5-10+ second loading times.
        """
        # Check cache first
        if self._is_arbitrable_pairs_cache_valid():
            logger.info("Returning cached arbitrable pairs")
            return self._arbitrable_pairs_cache
        
        # Prevent duplicate loading
        if self._loading_arbitrable_pairs:
            logger.info("Arbitrable pairs already loading, waiting...")
            # Wait for loading to complete
            while self._loading_arbitrable_pairs:
                await asyncio.sleep(0.1)
            
            # Check cache again after waiting
            if self._is_arbitrable_pairs_cache_valid():
                return self._arbitrable_pairs_cache
        
        # Load arbitrable pairs with performance optimization
        return await self._load_arbitrable_pairs_optimized()

    async def _load_arbitrable_pairs_optimized(self) -> Dict[str, List[str]]:
        """
        Optimized loading of arbitrable pairs with intelligent caching
        """
        self._loading_arbitrable_pairs = True
        start_time = time.time()
        
        try:
            logger.info("Loading arbitrable pairs with optimization...")
            
            # Create exchange objects efficiently
            exchange_names = list(SUPPORTED_EXCHANGES.values())
            exchanges = [self.get_saved_exchange(name) for name in exchange_names]
            
            # Load markets with caching and error handling
            await self._load_markets_with_caching(exchanges)
            
            # Process symbols efficiently
            pairs_exchanges_dict = await self._process_symbols_optimized(exchanges)
            
            # Update cache
            self._arbitrable_pairs_cache = pairs_exchanges_dict
            self._arbitrable_pairs_cache_time = time.time()
            
            load_time = time.time() - start_time
            logger.info(f"Arbitrable pairs loaded in {load_time:.2f}s, found {len(pairs_exchanges_dict)} pairs")
            
            return pairs_exchanges_dict
            
        except Exception as e:
            logger.error(f"Error loading arbitrable pairs: {e}")
            # Return empty dict instead of crashing
            return {}
        finally:
            self._loading_arbitrable_pairs = False

    async def _load_markets_with_caching(self, exchanges: List[ccxt.Exchange]) -> None:
        """
        Load markets for exchanges with intelligent caching to reduce API calls
        """
        tasks = []
        
        for exchange in exchanges:
            exchange_name = exchange.id
            
            # Check if markets are cached and valid
            if self._is_markets_cache_valid(exchange_name):
                logger.debug(f"Using cached markets for {exchange_name}")
                continue
            
            # Prevent duplicate loading
            if self._loading_markets.get(exchange_name, False):
                continue
                
            tasks.append(self._load_exchange_markets(exchange))
        
        if tasks:
            # Load markets in parallel with error handling
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    exchange_name = tasks[i].__self__.id if hasattr(tasks[i], '__self__') else "unknown"
                    logger.warning(f"Failed to load markets for {exchange_name}: {result}")

    async def _load_exchange_markets(self, exchange: ccxt.Exchange) -> None:
        """
        Load markets for a single exchange with caching
        """
        exchange_name = exchange.id
        self._loading_markets[exchange_name] = True
        
        try:
            logger.debug(f"Loading markets for {exchange_name}")
            await exchange.load_markets()
            
            # Cache the markets
            self._markets_cache[exchange_name] = exchange.markets
            self._markets_cache_time[exchange_name] = time.time()
            
            logger.debug(f"Loaded {len(exchange.markets)} markets for {exchange_name}")
            
        except Exception as e:
            logger.warning(f"Failed to load markets for {exchange_name}: {e}")
        finally:
            self._loading_markets[exchange_name] = False

    async def _process_symbols_optimized(self, exchanges: List[ccxt.Exchange]) -> Dict[str, List[str]]:
        """
        Process symbols efficiently to find arbitrable pairs
        """
        # Collect all symbols more efficiently
        all_symbols = []
        exchange_symbols = {}
        
        for exchange in exchanges:
            if hasattr(exchange, 'symbols') and exchange.symbols:
                symbols = list(exchange.symbols)
                all_symbols.extend(symbols)
                exchange_symbols[exchange.id] = set(symbols)
            else:
                logger.warning(f"No symbols found for {exchange.id}")
                exchange_symbols[exchange.id] = set()
        
        # Find symbols that appear on multiple exchanges more efficiently
        symbol_counts = {}
        for symbol in all_symbols:
            symbol_counts[symbol] = symbol_counts.get(symbol, 0) + 1
        
        arbitrable_symbols = [symbol for symbol, count in symbol_counts.items() if count > 1]
        arbitrable_symbols.sort()
        
        logger.info(f"Found {len(arbitrable_symbols)} arbitrable symbols")
        
        # Build pairs-exchanges mapping efficiently
        pairs_exchanges_dict: Dict[str, List[str]] = {}
        
        for symbol in arbitrable_symbols:
            supporting_exchanges = []
            
            for exchange_name, symbols_set in exchange_symbols.items():
                if symbol in symbols_set:
                    supporting_exchanges.append(exchange_name)
            
            if len(supporting_exchanges) > 1:
                pairs_exchanges_dict[symbol] = supporting_exchanges
        
        return pairs_exchanges_dict

    async def _ensure_markets_loaded(self, exchange: ccxt.Exchange) -> None:
        """
        Ensure markets are loaded for an exchange with caching
        """
        exchange_name = exchange.id
        
        if not self._is_markets_cache_valid(exchange_name):
            await self._load_exchange_markets(exchange)

    def _is_arbitrable_pairs_cache_valid(self) -> bool:
        """Check if arbitrable pairs cache is still valid"""
        if self._arbitrable_pairs_cache is None:
            return False
        
        age = time.time() - self._arbitrable_pairs_cache_time
        return age < self._arbitrable_pairs_cache_ttl

    def _is_markets_cache_valid(self, exchange_name: str) -> bool:
        """Check if markets cache is still valid for an exchange"""
        if exchange_name not in self._markets_cache:
            return False
        
        age = time.time() - self._markets_cache_time.get(exchange_name, 0)
        return age < self._markets_cache_ttl

    def get_saved_exchange(self, exchange: str) -> ccxt.Exchange:
        """Get or create exchange instance with caching"""
        if exchange not in self._exchanges:
            self._exchanges[exchange] = self.get_ccxt_exchange(exchange)
        return self._exchanges[exchange]

    def get_ccxt_exchange(self, exchange_name: str) -> ccxt.Exchange:
        """Create CCXT exchange instance"""
        try:
            return getattr(ccxt, exchange_name)()
        except AttributeError:
            logger.error(f"Unsupported exchange: {exchange_name}")
            # Return a default exchange or raise appropriate error
            raise ValueError(f"Unsupported exchange: {exchange_name}")

    async def close_all(self) -> None:
        """Close all exchange connections after completing async call"""
        if not self._exchanges:
            return

        tasks = []
        for exchange in self._exchanges.values():
            if hasattr(exchange, 'close'):
                tasks.append(exchange.close())

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    def clear_cache(self) -> None:
        """Clear all caches - useful for testing or forced refresh"""
        self._arbitrable_pairs_cache = None
        self._arbitrable_pairs_cache_time = 0
        self._markets_cache.clear()
        self._markets_cache_time.clear()
        logger.info("All caches cleared")

    def get_cache_stats(self) -> Dict:
        """Get cache statistics for monitoring"""
        return {
            "arbitrable_pairs_cached": self._arbitrable_pairs_cache is not None,
            "arbitrable_pairs_age": time.time() - self._arbitrable_pairs_cache_time if self._arbitrable_pairs_cache else 0,
            "markets_cached_exchanges": list(self._markets_cache.keys()),
            "total_cached_markets": sum(len(markets) for markets in self._markets_cache.values()),
        }
