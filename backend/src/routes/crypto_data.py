from fastapi import APIRouter, Depends
from routes.models.schemas import CompareRequest
from services.dependencies import call_manager_dependency 

crypto_router = APIRouter(prefix="/crypto")


@crypto_router.get("/ohlc")
async def get_klines_data(
    call_manager: call_manager_dependency,
    request: CompareRequest = Depends(),
) -> dict[str, list[dict[str, float | int]]]:
    return await call_manager.get_timeframe_aligned(request, "ohlc")


@crypto_router.get("/line-compare")
async def get_both_charts(
    call_manager: call_manager_dependency,
    request: CompareRequest = Depends(),
) -> dict[str, list[dict[str, int | float]]]:
    return await call_manager.get_timeframe_aligned(request, "chart_line")
