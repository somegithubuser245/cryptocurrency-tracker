from domain.models import BatchStatus, ComputedSpreadMax, CryptoPairName, SupportedExchangesByCrypto
from routes.models.schemas import BatchStatusResponse, ComputedSpreadResponse
from services.db_session import DBSessionDep
from sqlalchemy import select
from sqlalchemy.orm import aliased


def get_current_status(session: DBSessionDep) -> list[BatchStatusResponse]:
    """
    Get current batch processing status for all crypto pairs.
    Returns a list with crypto name, exchange name, interval, and status flags.
    """
    stmt = (
        select(
            CryptoPairName.crypto_name,
            SupportedExchangesByCrypto.supported_exchange,
            BatchStatus.interval,
            BatchStatus.saved_cache,
            BatchStatus.difference_found,
            BatchStatus.saved_db,
        )
        .join(SupportedExchangesByCrypto, BatchStatus.id == SupportedExchangesByCrypto.id)
        .join(CryptoPairName, BatchStatus.crypto_id == CryptoPairName.id)
        .order_by(CryptoPairName.crypto_name, SupportedExchangesByCrypto.supported_exchange)
    )

    results = session.execute(stmt).all()

    return [
        BatchStatusResponse(
            crypto_name=row.crypto_name,
            exchange=row.supported_exchange,
            interval=row.interval,
            cached=row.saved_cache,
            spread_computed=row.difference_found,
            saved_to_db=row.saved_db,
        )
        for row in results
    ]


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
            time=row.time,
            spread_percent=row.spread_percent,
            high_exchange=row.high_exchange,
            low_exchange=row.low_exchange,
        )
        for row in results
    ]
