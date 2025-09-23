import logging
from typing import Tuple

from domain.models import CryptoPairName, SupportedExchangesByCrypto
from services.db_session import DBSessionDep
from sqlalchemy import Row, Sequence, func, insert, select
from sqlalchemy.dialects.postgresql import insert as upsert

logger = logging.getLogger(__name__)

def insert_or_update_pairs(pairs: list[str], session: DBSessionDep) -> None:
    """
    Inserts or updates pairs.
    Returns list of all of the inserted ids

    Note:
    ----
    Doesn't return ids of already existing pairs
    """
    db_readable_dict = [{"crypto_name": pair} for pair in pairs]

    stmt = upsert(CryptoPairName)
    stmt = stmt.on_conflict_do_nothing(index_elements=["crypto_name"])
    crypto_ids = session.scalars(
        stmt.returning(CryptoPairName.id),
        db_readable_dict,
        execution_options={"populate_existing": True},
    ).all()
    session.commit()
    return crypto_ids


def insert_exchange_names(
        exchange_name: str,
        exchange_specific_symbols: list[str],
        session: DBSessionDep
    ) -> None:
    """
    Inserts a row with a crypto id and the corresponding
    supported exchange
    """
    all_crypto_ids = (
        session.execute(
            select(CryptoPairName.id).where(
                CryptoPairName.crypto_name.in_(exchange_specific_symbols)
            )
        )
        .scalars()
        .all()
    )

    db_readable_dict = [
        {"crypto_id": crypto_id, "supported_exchange": exchange_name}
        for crypto_id in all_crypto_ids
    ]
    try:
        stmt = insert(SupportedExchangesByCrypto).values(db_readable_dict)
        session.execute(stmt)
    except Exception as e:
        msg = f"Failed to insert exchange names for {exchange_name}"
        logger.exception(msg)
    session.commit()


def get_arbitrable_with_threshold(threshold: int, session: DBSessionDep) -> list[int]:
    """
    Find all pairs with at least @threshold available exchanges

    Returns
    ____
    The list of all crypto ids found
    """
    stmt = (
        select(SupportedExchangesByCrypto.crypto_id)
        .group_by(SupportedExchangesByCrypto.crypto_id)
        .having(func.count(SupportedExchangesByCrypto.crypto_id) >= threshold)
    )
    result = session.execute(stmt).scalars().all()
    return list(result)

def get_params_for_crypto_dto(
        ids_list: list[int],
        session: DBSessionDep
    ) -> Sequence[Row[Tuple[int, str, str]]]:
    """
    Returns tuples in following order:

    ID, name, supported exchange
    """
    stmt = (
        select(
            CryptoPairName.id,
            CryptoPairName.crypto_name,
            SupportedExchangesByCrypto.supported_exchange
        ).join(SupportedExchangesByCrypto,
               CryptoPairName.id == SupportedExchangesByCrypto.crypto_id
        ).where(CryptoPairName.id.in_(ids_list))
        .order_by(CryptoPairName.id)
    )
    return session.execute(stmt).all()
