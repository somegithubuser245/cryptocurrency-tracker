from sqlalchemy.orm import Session
from sqlalchemy import and_, select

from domain.models import BatchStatus, SupportedExchangesByCrypto

def get_exchange_name_by_id(session: Session, ce_id: int):
    stmt = select(SupportedExchangesByCrypto.supported_exchange).where(SupportedExchangesByCrypto.id == ce_id)
    return session.execute(stmt).one()

def scan_available_ohlc(session: Session, dtos_ids: list[int]):
    """
    Get all crypto with exchange ids
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

    grouped_ids_list = []
    for crypto_id in result_ids:
        stmt = select(BatchStatus.id).where(BatchStatus.crypto_id == crypto_id)
        grouped_ids_list.append(list(session.execute(stmt).scalars().all()))

    return grouped_ids_list