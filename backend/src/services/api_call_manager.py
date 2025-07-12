import asyncio
import json
import logging
import time
from typing import Dict, List, Any, Optional

from ..config.config import TickerType
from ..routes.models.schemas import CompareRequest, PriceTicketRequest
from .caching import Cacher
from .external_api_caller import CryptoFetcher
from ..utils.timeframes_equalizer import Equalizer
from ..utils.data_processor import DataProcessor

logger = logging.getLogger(__name__)

class ApiCallManager:
    """
    Optimized API call manager with aggressive caching and error handling
    """

    def __init__(self) -> None:
        self.equalizer = Equalizer()
        self.redis_cacher = Cacher()
        self.fetcher = CryptoFetcher()
        self.data_processor = DataProcessor(self.equalizer)  # Add data processor helper
        
        # In-memory cache for very recent requests (faster than Redis)
        self._memory_cache: Dict[str, Dict] = {}
        self._memory_cache_times: Dict[str, float] = {}
        self._memory_cache_ttl: float = 60  # 1 minute memory cache

    async def get_timeframe_aligned(
        self, request: CompareRequest, ticker_type: TickerType
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get timeframe-aligned data with aggressive caching and optimization
        """
        start_time = time.time()
        
        try:
            exchanges = [request.exchange1, request.exchange2]
            
            # Create requests for both exchanges
            requests = [
                PriceTicketRequest(
                    crypto_id=request.crypto_id, 
                    interval=request.interval, 
                    api_provider=exchange
                )
                for exchange in exchanges
            ]
            
            # Try to get data with caching
            data_sets_raw = await self._get_cached_data_parallel(requests)
            
            # Handle empty or invalid data
            if not all(data_sets_raw):
                logger.warning("Some data sets are empty, using fallback")
                data_sets_raw = await self._get_fallback_data(requests)
            
            # Use helper to process data - ELIMINATES DUPLICATION
            eq_data_exchange1, eq_data_exchange2, response_time = self.data_processor.process_chart_data(
                data_sets_raw, ticker_type, request, start_time
            )
            
            # Use helper to create response - ELIMINATES DUPLICATION  
            return self.data_processor.create_success_response(
                eq_data_exchange1, eq_data_exchange2, request
            )
            
        except Exception as e:
            # Use helper for error response - ELIMINATES DUPLICATION
            return self.data_processor.create_error_response(request, start_time, e)

    async def get_timeframe_aligned_with_metadata(
        self, request: CompareRequest, ticker_type: TickerType
    ) -> Dict[str, Any]:
        """
        Get timeframe-aligned data with metadata about data freshness and source
        """
        start_time = time.time()
        
        try:
            exchanges = [request.exchange1, request.exchange2]
            
            # Create requests for both exchanges
            requests = [
                PriceTicketRequest(
                    crypto_id=request.crypto_id, 
                    interval=request.interval, 
                    api_provider=exchange
                )
                for exchange in exchanges
            ]
            
            # Track cache hit information
            cache_info = {}
            data_sets_raw = []
            
            # Get data with cache tracking
            for req in requests:
                cache_key = self._generate_cache_key(req)
                cache_hit_type = "external_api"  # Default
                cache_age = 0
                
                # Check memory cache first
                memory_data = self._get_from_memory_cache(cache_key)
                if memory_data is not None:
                    data_sets_raw.append(memory_data)
                    cache_hit_type = "memory_cache"
                    cache_age = time.time() - self._memory_cache_times.get(cache_key, 0)
                else:
                    # Check Redis cache
                    try:
                        redis_data = self.redis_cacher.get(req)
                        if redis_data:
                            parsed_data = json.loads(redis_data)
                            data_sets_raw.append(parsed_data)
                            self._set_memory_cache(cache_key, parsed_data)
                            cache_hit_type = "redis_cache"
                            # Estimate cache age (we don't store exact timestamp in Redis)
                            cache_age = self._estimate_redis_cache_age(req.interval)
                        else:
                            # Fetch from external API
                            fresh_data = await self.fetcher.get_ohlc(req)
                            data_sets_raw.append(fresh_data)
                            await self._cache_fresh_data(req, fresh_data, cache_key)
                            cache_hit_type = "external_api"
                            cache_age = 0
                    except Exception as e:
                        logger.warning(f"Cache error, fetching fresh: {e}")
                        fresh_data = await self.fetcher.get_ohlc(req)
                        data_sets_raw.append(fresh_data)
                        cache_hit_type = "external_api"
                        cache_age = 0
                
                cache_info[req.api_provider.value] = {
                    "source": cache_hit_type,
                    "cache_age_seconds": round(cache_age, 2),
                    "last_external_fetch": self._get_estimated_last_fetch_time(cache_hit_type, cache_age),
                }
            
            # Handle empty or invalid data
            if not all(data_sets_raw):
                logger.warning("Some data sets are empty, using fallback")
                data_sets_raw = await self._get_fallback_data(requests)
                # Update cache info for fallback
                for i, req in enumerate(requests):
                    cache_info[req.api_provider.value] = {
                        "source": "external_api_fallback",
                        "cache_age_seconds": 0,
                        "last_external_fetch": time.time(),
                    }
            
            # Use helper to process data - ELIMINATES DUPLICATION
            eq_data_exchange1, eq_data_exchange2, response_time = self.data_processor.process_chart_data(
                data_sets_raw, ticker_type, request, start_time
            )
            
            # Get cache TTL for metadata
            cache_ttl_seconds = self._get_cache_ttl(request.interval)
            
            # Use helper to create metadata response - ELIMINATES DUPLICATION
            return self.data_processor.create_metadata_response(
                eq_data_exchange1, eq_data_exchange2, request, response_time, 
                cache_info, cache_ttl_seconds
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            # Use helper for metadata error response - ELIMINATES DUPLICATION
            return self.data_processor.create_metadata_error_response(request, response_time, e)

    async def _get_cached_data_parallel(self, requests: List[PriceTicketRequest]) -> List[List]:
        """
        Get data for multiple requests in parallel with multi-level caching
        """
        tasks = []
        
        for request in requests:
            tasks.append(self._get_single_cached_data(request))
        
        # Execute all requests in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions in individual requests
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Request {i} failed: {result}")
                processed_results.append([])  # Empty data for failed request
            else:
                processed_results.append(result)
        
        return processed_results

    async def _get_single_cached_data(self, request: PriceTicketRequest) -> List:
        """
        Get data for a single request with multi-level caching
        """
        cache_key = self._generate_cache_key(request)
        
        # Level 1: Memory cache (fastest)
        memory_data = self._get_from_memory_cache(cache_key)
        if memory_data is not None:
            logger.debug(f"Memory cache hit for {cache_key}")
            return memory_data
        
        # Level 2: Redis cache
        try:
            redis_data = self.redis_cacher.get(request)
            if redis_data:
                logger.debug(f"Redis cache hit for {cache_key}")
                parsed_data = json.loads(redis_data)
                self._set_memory_cache(cache_key, parsed_data)
                return parsed_data
        except Exception as e:
            logger.warning(f"Redis cache error for {cache_key}: {e}")
        
        # Level 3: Fetch from external API
        try:
            logger.debug(f"Fetching fresh data for {cache_key}")
            fresh_data = await self.fetcher.get_ohlc(request)
            
            # Cache the fresh data
            await self._cache_fresh_data(request, fresh_data, cache_key)
            
            return fresh_data
            
        except Exception as e:
            logger.error(f"Failed to fetch data for {cache_key}: {e}")
            return []

    async def _cache_fresh_data(self, request: PriceTicketRequest, data: List, cache_key: str) -> None:
        """
        Cache fresh data in both Redis and memory
        """
        try:
            # Cache in Redis with appropriate TTL
            ttl = self._get_cache_ttl(request.interval)
            data_json = json.dumps(data)
            self.redis_cacher.set(data_json, request, ttl)
            
            # Cache in memory
            self._set_memory_cache(cache_key, data)
            
        except Exception as e:
            logger.warning(f"Failed to cache data for {cache_key}: {e}")

    def _get_cache_ttl(self, interval: str) -> int:
        """
        Get appropriate cache TTL based on interval
        """
        ttl_map = {
            "1m": 60,      # 1 minute data cached for 1 minute
            "5m": 300,     # 5 minute data cached for 5 minutes  
            "15m": 900,    # 15 minute data cached for 15 minutes
            "30m": 1800,   # 30 minute data cached for 30 minutes
            "1h": 3600,    # 1 hour data cached for 1 hour
            "4h": 7200,    # 4 hour data cached for 2 hours
            "1d": 21600,   # 1 day data cached for 6 hours
            "1w": 86400,   # 1 week data cached for 1 day
        }
        return ttl_map.get(interval, 3600)  # Default 1 hour

    def _generate_cache_key(self, request: PriceTicketRequest) -> str:
        """Generate cache key for request"""
        return f"{request.api_provider.value}:{request.crypto_id}:{request.interval}"

    def _get_from_memory_cache(self, cache_key: str) -> Optional[List]:
        """Get data from memory cache if valid"""
        if cache_key not in self._memory_cache:
            return None
        
        # Check if cache is still valid
        age = time.time() - self._memory_cache_times.get(cache_key, 0)
        if age > self._memory_cache_ttl:
            # Clean up expired cache
            self._memory_cache.pop(cache_key, None)
            self._memory_cache_times.pop(cache_key, None)
            return None
        
        return self._memory_cache[cache_key]

    def _set_memory_cache(self, cache_key: str, data: List) -> None:
        """Set data in memory cache"""
        self._memory_cache[cache_key] = data
        self._memory_cache_times[cache_key] = time.time()

    async def _get_fallback_data(self, requests: List[PriceTicketRequest]) -> List[List]:
        """
        Get fallback data when cached data fails
        """
        logger.info("Using fallback data fetching")
        
        fallback_results = []
        for request in requests:
            try:
                data = await self.fetcher.get_ohlc(request)
                fallback_results.append(data if data else [])
            except Exception as e:
                logger.error(f"Fallback failed for {request.api_provider}: {e}")
                fallback_results.append([])
        
        return fallback_results

    def _estimate_redis_cache_age(self, interval: str) -> float:
        """Estimate cache age for Redis data based on interval"""
        # Since we don't store exact timestamps in Redis, estimate based on TTL
        ttl = self._get_cache_ttl(interval)
        # Assume data is on average half the TTL age
        return ttl / 2

    def _get_estimated_last_fetch_time(self, cache_type: str, cache_age: float) -> float:
        """Get estimated timestamp of last external API fetch"""
        if cache_type == "external_api":
            return time.time()  # Just fetched
        else:
            return time.time() - cache_age  # Fetched cache_age seconds ago

    def clear_memory_cache(self) -> None:
        """Clear memory cache - useful for debugging"""
        self._memory_cache.clear()
        self._memory_cache_times.clear()
        logger.info("Memory cache cleared")

    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        return {
            "memory_cache_size": len(self._memory_cache),
            "memory_cache_keys": list(self._memory_cache.keys()),
        }