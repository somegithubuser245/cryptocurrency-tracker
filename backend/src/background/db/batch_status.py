from domain.models import BatchStatus, ComputedSpreadMax
from services.db_session import DBSessionDep
from sqlalchemy import delete, insert, update


def init_batch_status(
    session: DBSessionDep,
    ids_by_exchange: list[int],
    crypto_ids: list[int],
    interval: str,
) -> None:
    """
    Initialize batch status table
    """
    db_readable_dict = [
        {
            "id": id_by_exchange,
            "crypto_id": crypto_id,
            "interval": interval,
            "saved_cache": False,
            "difference_found": False,
            "saved_db": False,
        }
        for id_by_exchange, crypto_id in zip(ids_by_exchange, crypto_ids, strict=True)
    ]
    stmt = insert(BatchStatus).values(db_readable_dict)
    session.execute(stmt)
    session.commit()


def update_batch_status_cached(
    session: DBSessionDep,
    ce_ids: list[int],
) -> None:
    """
    Update status field for cache
    """
    stmt = update(BatchStatus).where(BatchStatus.id.in_(ce_ids)).values({"saved_cache": True})
    session.execute(stmt)
    session.commit()


def delete_tables(
    session: DBSessionDep,
) -> None:
    """
    Method to delete Tables used for Batch Status and saved Computed spread
    """
    stmt = delete(BatchStatus)
    session.execute(stmt)
    session.flush()
    stmt = delete(ComputedSpreadMax)
    session.execute(stmt)
    session.commit()
