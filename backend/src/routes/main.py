from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .crypto_data import crypto_router
from .static_data import static_router
from ..services.api_call_manager import ApiCallManager

# Setup
app = FastAPI(title="Cryptocurrency Tracker API", version="1.0.0")
api_call_manager = ApiCallManager()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring and diagnostics"""
    return {"status": "healthy", "message": "Crypto tracker backend is running"}

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Cryptocurrency Tracker API", "version": "1.0.0"}

@app.get("/performance")
async def get_performance_stats():
    """Get performance statistics for monitoring"""
    try:
        from .static_data import get_crypto_fetcher
        fetcher = get_crypto_fetcher()
        cache_stats = fetcher.get_cache_stats()
        
        return {
            "status": "ok",
            "cache_stats": cache_stats,
            "message": "Performance statistics"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

app.include_router(static_router)
app.include_router(crypto_router)

@app.on_event("startup")
async def startup():
    """Initialize data on server startup"""
    try:
        from .static_data import startup_event
        await startup_event()
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Startup event failed: {e}")

@app.exception_handler(ValueError)
async def validation_exception_handler(request: Request, exc: ValueError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": str(exc)})
