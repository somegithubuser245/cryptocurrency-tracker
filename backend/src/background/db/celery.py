from sqlalchemy.orm import Session
from sqlalchemy import and_, insert, select

from domain.models import BatchStatus, ComputedSpreadMax, SupportedExchangesByCrypto

def get_exchange_name_by_id(session: Session, ce_id: int):
    stmt = select(SupportedExchangesByCrypto.supported_exchange).where(SupportedExchangesByCrypto.id == ce_id)
    return session.execute(stmt).one()

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
    stmt = (select(BatchStatus.crypto_id)
            .where(
                and_(BatchStatus.id.in_(dtos_ids),
                     BatchStatus.saved_cache == True
                    )
            )
    )
    
    result_ids = session.execute(stmt).scalars().unique().all()
    return result_ids

def insert_computed_spread(session: Session, computed_ohlc: dict):
    """
    Insert rows with computed ohlc straight from pandas
    """
    insert(ComputedSpreadMax).values(computed_ohlc)
    session.commit()

