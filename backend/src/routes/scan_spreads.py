import logging

from background.batch_fetch_ohlc import BatchFetcherDependency
from background.db.user_api import get_batch_status_counts, get_computed_spreads
from fastapi import APIRouter, BackgroundTasks
from routes.models.schemas import (
    BatchStatusSummaryResponse,
    ComputedSpreadResponse,
    TaskStatusResponse,
)
from services.db_session import DBSessionDep

logger = logging.getLogger(__name__)
spreads_router = APIRouter(prefix="/spreads")


@spreads_router.post("/init-pairs")
async def init_pairs(
    batch_fetcher: BatchFetcherDependency,
) -> bool:
    """
    Initialize crypto pairs and supported exchanges in the database.
    """
    # no bg tasks used, as we need to know if
    # pairs were sucessfully initted
    return await batch_fetcher.init_pairs_db()


@spreads_router.post("/compute-all")
async def get_all_spreads(
    batch_fetcher: BatchFetcherDependency,
    bg_tasks: BackgroundTasks,
) -> TaskStatusResponse:
    """
    Trigger background task to download all OHLC data for arbitrable pairs.
    """
    bg_tasks.add_task(batch_fetcher.download_all_ohlc)
    return TaskStatusResponse(status="success", message="Batch OHLC download started")


@spreads_router.get("/batch-status")
def get_status(db: DBSessionDep) -> BatchStatusSummaryResponse:
    """
    Get aggregate batch processing status summary.

    Returns:
        Summary object containing:
        - total_pairs: Total number of crypto-exchange pairs being tracked
        - cached: Number of pairs with OHLC data cached in Redis
        - spreads_computed: Number of pairs with computed spreads
        - processing_progress: Percentage of pairs cached (0-100)
    """
    counts = get_batch_status_counts(session=db)

    # Calculate progress percentage
    total = counts["total_pairs"]
    cached = counts["cached"]
    progress = (cached / total * 100.0) if total > 0 else 0.0

    return BatchStatusSummaryResponse(
        total_pairs=total,
        cached=cached,
        spreads_computed=counts["spreads_computed"],
        processing_progress=round(progress, 2),
    )


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
