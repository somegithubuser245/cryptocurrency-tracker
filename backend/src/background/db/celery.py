from domain.models import BatchStatus, ComputedSpreadMax
from sqlalchemy import and_, func, insert, select, update
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert as upsert


def get_ce_ids_by_crypto_id(session: Session, crypto_id: int) -> list[int]:
    """
    Get all crypto with exchange ids

    From status table, based on unique crypto id

    No filtering applied!
    """

    stmt = select(BatchStatus.id).where(BatchStatus.crypto_id == crypto_id)
    return list(session.execute(stmt).scalars().all())


def scan_available_ohlc(session: Session, dtos_ids: list[int]) -> list[int]:
    """
    Get all cached unique crypto ids where ALL exchanges have been cached.

    First extracts unique crypto_ids from the provided dtos_ids batch,
    then checks if ALL exchanges for those cryptos are cached (not just the ones in current batch).

    This solves the edge case where OHLC for the same crypto is split across batches.

    Additionally filters out already-computed cryptos (difference_found=True) to prevent
    multiple worker chains from computing the same crypto when tasks execute out of order.
    """
    # Step 1: Get unique crypto_ids from the current batch
    crypto_ids_subq = select(BatchStatus.crypto_id).where(BatchStatus.id.in_(dtos_ids)).distinct()

    # Step 2: For each crypto_id, check if ALL its exchanges are cached
    # AND none have been marked as computed yet
    stmt = (
        select(BatchStatus.crypto_id)
        .where(BatchStatus.crypto_id.in_(crypto_ids_subq))
        .group_by(BatchStatus.crypto_id)
        .having(
            and_(
                # All exchanges for this crypto must have saved_cache=True
                func.bool_and(BatchStatus.saved_cache) == True,  # noqa: E712
                func.bool_and(BatchStatus.difference_found) == False,  # noqa: E712
            )
        )
    )

    result_ids = session.execute(stmt).scalars().all()
    return list(result_ids)


def save_compute_mark_complete(
    session: Session,
    crypto_id: int,
    computed_spread: dict,
) -> None:
    """
    Insert rows with computed ohlc straight from pandas
    Uses UPSERT (ON CONFLICT) to handle race conditions when multiple workers
    try to compute the same crypto_id simultaneously.
    """
    values_with_id = {"id": crypto_id, **computed_spread}

    stmt_insert = (
        upsert(ComputedSpreadMax)
        .values(values_with_id)
        .on_conflict_do_update(
            index_elements=["id"],
            set_=computed_spread,  # Update with new spread data if already exists
        )
    )
    session.execute(stmt_insert)
    session.flush()

    stmt_update_status = (
        update(BatchStatus).where(BatchStatus.crypto_id == crypto_id).values(difference_found=True)
    )
    session.execute(stmt_update_status)
    session.commit()
