from background.all_pairs_historical_spread import get_them_pairs
from fastapi import APIRouter
from routes.models.schemas import PriceTicker
from utils.dependencies.dependencies import data_manager_dependency, spreads_calculator_dependency

spreads_router = APIRouter(prefix="/spreads")

@spreads_router.post("/per-ticker/all")
async def get_spreads(
    spr_calc: spreads_calculator_dependency,
    ticker: PriceTicker
) -> dict:
    spread = await spr_calc.create(ticker)
    return spread.get_as_dict()

@spreads_router.post("/per-ticker/max")
async def get_max_spread(
    spr_calc: spreads_calculator_dependency,
    ticker: PriceTicker
) -> dict:
    spread = await spr_calc.create(ticker)
    return spread.get_max_spread()

@spreads_router.get("/all-at-once")
async def get_all_spreads(
    data_manager: data_manager_dependency,
    spr_calc: spreads_calculator_dependency
) -> dict:
    spreads = await get_them_pairs(
        data_manager,
        spr_calc
    )
    return spreads
