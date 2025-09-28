from domain.models import BatchStatus, ComputedSpreadMax
from sqlalchemy import and_, insert, select, update
from sqlalchemy.orm import Session


def get_ce_ids_by_crypto_id(session: Session, crypto_id: int) -> list[int]:
    """
    Get all crypto with exchange ids

    From status table, based on unique crypto id

    No filtering applied!
    """

    stmt = select(BatchStatus.id).where(BatchStatus.crypto_id == crypto_id)
    return list(session.execute(stmt).scalars().all())


def scan_available_ohlc(session: Session, dtos_ids: list[int]):
    """
    Get all cached unique crypto ids
    Grouped by crypto id
    """
    stmt = select(BatchStatus.crypto_id).where(
        and_(BatchStatus.id.in_(dtos_ids), BatchStatus.saved_cache == True)  # noqa: E712 sqlachemy specific
    )

    result_ids = session.execute(stmt).scalars().unique().all()
    return result_ids


def mark_as_completed(session: Session, crypto_id: int):
    stmt = (
        update(BatchStatus.difference_found).where(BatchStatus.crypto_id == crypto_id).values(True)
    )
    session.execute(stmt)
    session.commit()


def insert_computed_spread(session: Session, computed_ohlc: dict):
    """
    Insert rows with computed ohlc straight from pandas
    """
    stmt = insert(ComputedSpreadMax).values(computed_ohlc)
    session.execute(stmt)
    session.commit()
