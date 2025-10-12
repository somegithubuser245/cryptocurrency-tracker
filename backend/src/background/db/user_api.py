from domain.models import BatchStatus, ComputedSpreadMax, CryptoPairName, SupportedExchangesByCrypto
from routes.models.schemas import ComputedSpreadResponse
from services.db_session import DBSessionDep
from sqlalchemy import Integer, func, select
from sqlalchemy.orm import aliased
from utils.dependencies.timestamp_norm import normalize_timestamp


def get_batch_status_counts(session: DBSessionDep) -> dict[str, int]:
    """
    Get aggregate counts for batch processing status.
    Returns dictionary with total, cached, and spreads_computed counts.
    """
    stmt = select(
        func.count(BatchStatus.id).label("total"),
        func.sum(func.cast(BatchStatus.saved_cache, Integer)).label("cached"),
        func.sum(func.cast(BatchStatus.difference_found, Integer)).label("spreads_computed"),
    )

    result = session.execute(stmt).one()

    return {
        "total_pairs": result.total or 0,
        "cached": result.cached or 0,
        "spreads_computed": result.spreads_computed or 0,
    }


def get_computed_spreads(session: DBSessionDep) -> list[ComputedSpreadResponse]:
    """
    Get all computed spreads with exchange names resolved.
    Returns list with crypto name, timestamp, spread percent, and exchange names.
    """
    # Create aliases for the two joins to SupportedExchangesByCrypto
    high_exchange = aliased(SupportedExchangesByCrypto)
    low_exchange = aliased(SupportedExchangesByCrypto)

    stmt = (
        select(
            CryptoPairName.crypto_name,
            ComputedSpreadMax.time,
            ComputedSpreadMax.spread_percent,
            high_exchange.supported_exchange.label("high_exchange"),
            low_exchange.supported_exchange.label("low_exchange"),
        )
        .join(CryptoPairName, ComputedSpreadMax.id == CryptoPairName.id)
        .join(high_exchange, ComputedSpreadMax.high_exchange_id == high_exchange.id)
        .join(low_exchange, ComputedSpreadMax.low_exchange_id == low_exchange.id)
        .order_by(ComputedSpreadMax.spread_percent.desc())
    )

    results = session.execute(stmt).all()

    return [
        ComputedSpreadResponse(
            crypto_name=row.crypto_name,
            time=normalize_timestamp(row.time),
            spread_percent=row.spread_percent,
            high_exchange=row.high_exchange,
            low_exchange=row.low_exchange,
        )
        for row in results
    ]
