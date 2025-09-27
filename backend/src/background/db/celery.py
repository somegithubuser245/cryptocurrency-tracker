from sqlalchemy.orm import Session
from sqlalchemy import select

from domain.models import BatchStatus

def scan_available_ohlc(session: Session, dtos_ids: list[int]):
    """
    Get the amount of pairs found with initial dtos
    """
    stmt = select(BatchStatus.id).where(BatchStatus.id.in_(dtos_ids))
    return session.execute(stmt).scalars().all()