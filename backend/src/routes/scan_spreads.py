from fastapi import APIRouter

from routes.models.schemas import PriceTickerRequest
from services.dependencies import spreads_calculator_dependency

spreads_router = APIRouter(prefix="/spreads")

@spreads_router.post("/per-ticker/all")
async def get_spreads(
    spr_calc: spreads_calculator_dependency,
    ticker: PriceTickerRequest
) -> dict:
    spread = await spr_calc.create(ticker)
    return spread.get_as_dict()

@spreads_router.post("/per-ticker/max")
async def get_max_spread(
    spr_calc: spreads_calculator_dependency,
    ticker: PriceTickerRequest
) -> dict:
    spread = await spr_calc.create(ticker)
    return spread.get_max_spread()
    