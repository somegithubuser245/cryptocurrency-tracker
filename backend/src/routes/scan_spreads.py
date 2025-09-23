import logging

from background.batch_fetch_ohlc import BatchFetcherDependency
from fastapi import APIRouter, BackgroundTasks
from services.db_session import DBSessionDep

logger = logging.getLogger(__name__)
spreads_router = APIRouter(prefix="/spreads")


@spreads_router.get("/all-at-once")
async def get_all_spreads(
    batch_fetcher: BatchFetcherDependency,
    bg_tasks: BackgroundTasks,
) -> dict:
    bg_tasks.add_task(batch_fetcher.download_all_ohlc())
    return {"background task added": True}


@spreads_router.post("/init-pairs")
async def init_pairs(
    batch_fetcher: BatchFetcherDependency,
    bg_tasks: BackgroundTasks,
    db: DBSessionDep
) -> dict:
    bg_tasks.add_task(batch_fetcher.init_pairs_db, db)
    return {"pairs init process started": True}