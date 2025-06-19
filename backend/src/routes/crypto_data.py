from fastapi import APIRouter, Query
from routes.models.schemas import CompareRequest
from services.api_call_manager import ApiCallManager

crypto_router = APIRouter(prefix="/crypto")


@crypto_router.get("/ohlc")
async def get_klines_data(
    request: CompareRequest = Query(),  # noqa: B008
) -> dict[str, list[dict[str, float | int]]]:
    return await ApiCallManager().get_timeframe_aligned(request, "ohlc")


@crypto_router.get("/line-compare")
async def get_both_charts(
    request: CompareRequest = Query(),
) -> dict[str, list[dict[str, int | float]]]:
    return await ApiCallManager().get_timeframe_aligned(request, "chart_line")
