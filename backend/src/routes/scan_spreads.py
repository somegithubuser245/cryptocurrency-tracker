import logging

from background.batch_fetch_ohlc import BatchFetcherDependency
from background.db.user_api import get_computed_spreads, get_current_status
from fastapi import APIRouter, BackgroundTasks
from routes.models.schemas import BatchStatusResponse, ComputedSpreadResponse, TaskStatusResponse
from services.db_session import DBSessionDep

logger = logging.getLogger(__name__)
spreads_router = APIRouter(prefix="/spreads")


@spreads_router.post("/all-at-once")
async def get_all_spreads(
    batch_fetcher: BatchFetcherDependency,
    db: DBSessionDep,
    bg_tasks: BackgroundTasks,
) -> TaskStatusResponse:
    """
    Trigger background task to download all OHLC data for arbitrable pairs.
    """
    bg_tasks.add_task(batch_fetcher.download_all_ohlc, db)
    return TaskStatusResponse(status="success", message="Batch OHLC download started")


@spreads_router.post("/init-pairs")
async def init_pairs(
    batch_fetcher: BatchFetcherDependency,
    bg_tasks: BackgroundTasks,
    db: DBSessionDep,
) -> TaskStatusResponse:
    """
    Initialize crypto pairs and supported exchanges in the database.
    """
    bg_tasks.add_task(batch_fetcher.init_pairs_db, db)
    return TaskStatusResponse(status="success", message="Pairs initialization started")


@spreads_router.get("/batch-status")
def get_status(db: DBSessionDep) -> list[BatchStatusResponse]:
    """
    Get current batch processing status for all crypto pairs.

    Returns:
        List of status objects containing:
        - crypto_name: Name of the cryptocurrency pair
        - exchange: Exchange name
        - interval: Time interval being processed
        - cached: Whether OHLC data is cached in Redis
        - spread_computed: Whether spread has been computed
        - saved_to_db: Whether result is saved to database
    """
    return get_current_status(session=db)


@spreads_router.get("/computed")
def get_computed_spreads_endpoint(db: DBSessionDep) -> list[ComputedSpreadResponse]:
    """
    Get all computed spreads with exchange names resolved.

    Returns:
        List of computed spread objects containing:
        - crypto_name: Name of the cryptocurrency pair
        - time: Timestamp of maximum spread (ISO format)
        - spread_percent: Spread percentage
        - high_exchange: Exchange with higher price (sell here)
        - low_exchange: Exchange with lower price (buy here)

    Results are ordered by spread_percent in descending order.
    """
    return get_computed_spreads(session=db)
