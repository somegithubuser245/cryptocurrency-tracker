from background.batch_fetch_ohlc import BatchFetcherDependency
from fastapi import APIRouter, BackgroundTasks
from routes.models.schemas import PriceTicker
from utils.dependencies.dependencies import spreads_calculator_dependency

spreads_router = APIRouter(prefix="/spreads")


@spreads_router.post("/per-ticker/all")
async def get_spreads(spr_calc: spreads_calculator_dependency, ticker: PriceTicker) -> dict:
    spread = await spr_calc.create(ticker)
    return spread.get_as_dict()


@spreads_router.post("/per-ticker/max")
async def get_max_spread(spr_calc: spreads_calculator_dependency, ticker: PriceTicker) -> dict:
    spread = await spr_calc.create(ticker)
    return spread.get_max_spread()


@spreads_router.get("/all-at-once")
async def get_all_spreads(
    batch_fetcher: BatchFetcherDependency,
    bg_tasks: BackgroundTasks,
) -> dict:
    bg_tasks.add_task(batch_fetcher.download_all_in_chunks)
    return {"background task added": True}
