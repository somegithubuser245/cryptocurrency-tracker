import logging
from typing import Tuple

from domain.models import CryptoPairName, SupportedExchangesByCrypto
from services.db_session import DBSessionDep
from sqlalchemy import Row, Sequence, func, select
from sqlalchemy.dialects.postgresql import insert as upsert

logger = logging.getLogger(__name__)


def insert_or_update_pairs(pairs: list[str], session: DBSessionDep) -> None:
    """
    Inserts or updates pairs.
    """
    db_readable_dict = [{"crypto_name": pair} for pair in pairs]

    stmt = (
        upsert(CryptoPairName)
        .values(db_readable_dict)
        .on_conflict_do_nothing(index_elements=["crypto_name"])
    )
    session.execute(stmt)
    session.commit()


def insert_exchange_names(exchange_name: str, crypto_ids: list[str], session: DBSessionDep) -> None:
    """
    Inserts a row with a crypto id and the corresponding
    supported exchange

    Makes use of postgres insert or update (upsert)
    """
    all_crypto_ids = (
        session.execute(select(CryptoPairName.id).where(CryptoPairName.crypto_name.in_(crypto_ids)))
        .scalars()
        .all()
    )

    db_readable_dict = [
        {"crypto_id": crypto_id, "supported_exchange": exchange_name}
        for crypto_id in all_crypto_ids
    ]
    try:
        stmt = (
            upsert(SupportedExchangesByCrypto)
            .values(db_readable_dict)
            .on_conflict_do_nothing(constraint="unique_id_to_exchange")
        )
        session.execute(stmt)
        session.commit()
    except Exception:
        msg = f"Failed to insert exchange names for {exchange_name}"
        logger.exception(msg)


def get_arbitrable_rows(threshold: int, session: DBSessionDep) -> list[SupportedExchangesByCrypto]:
    """
    Find all pairs with at least @threshold available exchanges

    Returns
    ____
    The list of all crypto ids found
    """
    stmt = (
        select(SupportedExchangesByCrypto.crypto_id)
        .group_by(
            SupportedExchangesByCrypto.crypto_id,
        )
        .having(func.count(SupportedExchangesByCrypto.crypto_id) >= threshold)
    )
    result = session.execute(stmt).scalars().all()

    stmt = select(SupportedExchangesByCrypto).where(
        SupportedExchangesByCrypto.crypto_id.in_(result)
    )
    return session.execute(stmt).scalars().all()


def get_params_for_crypto_dto(
    ids_list: list[int], session: DBSessionDep
) -> Sequence[Row[Tuple[int, str, str]]]:
    """
    Returns tuples in following order:

    ID, name, supported exchange
    """
    stmt = (
        select(
            SupportedExchangesByCrypto.id,
            CryptoPairName.crypto_name,
            SupportedExchangesByCrypto.supported_exchange,
        )
        .join(CryptoPairName, CryptoPairName.id == SupportedExchangesByCrypto.crypto_id)
        .where(SupportedExchangesByCrypto.id.in_(ids_list))
        # the order in which the ids are returned is very important
        # we must order by id to have different exchanges for an id first
        # otherwise we'll have all crypto pairs for one exchange only first
        # which isn't useful if we're comparing ohlc between different exchanges
        .order_by(CryptoPairName.id)
    )
    return session.execute(stmt).all()
