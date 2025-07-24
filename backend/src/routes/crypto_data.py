from fastapi import APIRouter, Query
from routes.models.schemas import CompareRequest
from services.api_call_manager import ApiCallManager

crypto_router = APIRouter(prefix="/crypto")

api_call_manager = ApiCallManager()


@crypto_router.get("/ohlc")
async def get_klines_data(
    request: CompareRequest = Query(),  # noqa: B008
) -> dict[str, list[dict[str, float | int]]]:
    return await api_call_manager.get_timeframe_aligned(request, "ohlc")


@crypto_router.get("/line-compare")
async def get_both_charts(
    request: CompareRequest = Query(),  # noqa: B008
) -> dict[str, list[dict[str, int | float]]]:
    return await api_call_manager.get_timeframe_aligned(request, "chart_line")
