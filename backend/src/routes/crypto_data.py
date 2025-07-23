import time
from fastapi import APIRouter, Query
from .models.schemas import CompareRequest
from ..services.api_call_manager import ApiCallManager
from ..config.config import TickerType

crypto_router = APIRouter(prefix="/crypto")

api_call_manager = ApiCallManager()


@crypto_router.get("/ohlc")
async def get_klines_data(
    request: CompareRequest = Query(),  # noqa: B008
) -> dict:
    """Get OHLC data with metadata about data freshness and source"""
    data = await api_call_manager.get_timeframe_aligned_with_metadata(request, TickerType.OHLC)
    return data


@crypto_router.get("/line-compare")
async def get_both_charts(
    request: CompareRequest = Query(),
) -> dict:
    """Get chart comparison data with metadata about data freshness and source"""
    data = await api_call_manager.get_timeframe_aligned_with_metadata(request, TickerType.CHART_LINE)
    return data
