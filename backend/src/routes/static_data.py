import asyncio
import logging
import time
from fastapi import APIRouter, BackgroundTasks
from fastapi.responses import JSONResponse
from .models.schemas import config_types
from ..services.external_api_caller import CryptoFetcher

logger = logging.getLogger(__name__)

static_router = APIRouter(prefix="/static")

# Create crypto fetcher instance (will be initialized on first use)
crypto_fetcher = None

def get_crypto_fetcher():
    """Get or create crypto fetcher instance"""
    global crypto_fetcher
    if crypto_fetcher is None:
        crypto_fetcher = CryptoFetcher()
    return crypto_fetcher

@static_router.get("/config/{config_type}")
async def get_config(config_type: str) -> dict:
    """
    Get configuration data with instant responses for static data
    """
    start_time = time.time()
    
    try:
        config_data = config_types.get(config_type)
        
        if config_data is None:
            logger.warning(f"Configuration type '{config_type}' not found")
            return {"error": f"Configuration type '{config_type}' not found"}
        
        response_time = time.time() - start_time
        logger.info(f"Config '{config_type}' served in {response_time:.3f}s")
        
        return config_data
        
    except Exception as e:
        logger.error(f"Error serving config '{config_type}': {e}")
        return {"error": "Internal server error"}

@static_router.get("/pairs-exchanges")
async def get_pairs_exchanges_dict() -> dict:
    """
    Get pairs-exchanges mapping with aggressive caching
    
    This endpoint was the main performance bottleneck causing 5-10+ second load times.
    Now optimized with caching to reduce external API calls.
    """
    start_time = time.time()
    
    try:
        logger.info("Fetching arbitrable pairs with caching...")
        
        # Use the optimized crypto fetcher with caching
        fetcher = get_crypto_fetcher()
        pairs_exchanges = await fetcher.get_arbitrable_pairs()
        
        response_time = time.time() - start_time
        logger.info(f"Pairs-exchanges served in {response_time:.2f}s, {len(pairs_exchanges)} pairs")
        
        return pairs_exchanges
        
    except Exception as e:
        logger.error(f"Error fetching pairs-exchanges: {e}")
        response_time = time.time() - start_time
        logger.error(f"Failed after {response_time:.2f}s")
        
        # Return empty dict instead of crashing
        return {}

@static_router.get("/cache/status")
async def get_cache_status():
    """
    Get cache status for monitoring and debugging
    """
    try:
        fetcher = get_crypto_fetcher()
        cache_stats = fetcher.get_cache_stats()
        return {
            "status": "ok",
            "cache_stats": cache_stats,
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"Error getting cache status: {e}")
        return {"status": "error", "message": str(e)}

@static_router.post("/cache/clear")
async def clear_cache():
    """
    Clear all caches - useful for forced refresh
    """
    try:
        fetcher = get_crypto_fetcher()
        fetcher.clear_cache()
        return {"status": "ok", "message": "All caches cleared"}
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        return {"status": "error", "message": str(e)}

@static_router.post("/cache/warm")
async def warm_cache(background_tasks: BackgroundTasks):
    """
    Warm up the cache in background for better performance
    """
    try:
        background_tasks.add_task(_warm_cache_background)
        return {"status": "ok", "message": "Cache warming started in background"}
    except Exception as e:
        logger.error(f"Error starting cache warm: {e}")
        return {"status": "error", "message": str(e)}

async def _warm_cache_background():
    """
    Background task to warm up caches
    """
    try:
        logger.info("Starting cache warm-up...")
        start_time = time.time()
        
        # Pre-load arbitrable pairs to warm cache
        fetcher = get_crypto_fetcher()
        await fetcher.get_arbitrable_pairs()
        
        warm_time = time.time() - start_time
        logger.info(f"Cache warm-up completed in {warm_time:.2f}s")
        
    except Exception as e:
        logger.error(f"Error during cache warm-up: {e}")

# Startup event to pre-warm caches
async def startup_event():
    """
    Called during server startup to pre-warm caches
    """
    try:
        logger.info("Pre-warming caches on startup...")
        
        # Start cache warming in background to not block startup
        asyncio.create_task(_warm_cache_background())
        
    except Exception as e:
        logger.error(f"Error during startup cache warming: {e}")
