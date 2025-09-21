from domain.models import CryptoPairName, SupportedExchangesByCrypto
from services.db_session import Session
from sqlalchemy import insert, select
from sqlalchemy.dialects.postgresql import insert as upsert


def insert_or_update_pairs(pairs: list[str]) -> None:
    """
    Inserts or updates pairs.
    Returns list of all of the ids present in the table
    """
    db_readable_dict = [{"crypto_name": pair} for pair in pairs]

    with Session() as session:
        stmt = upsert(CryptoPairName)
        stmt = stmt.on_conflict_do_nothing(index_elements=["crypto_name"])
        crypto_ids = session.scalars(
            stmt.returning(CryptoPairName.id),
            db_readable_dict,
            execution_options={"populate_existing": True},
        ).all()
        session.commit()
        return crypto_ids


def insert_exchange_names(exchange_name: str, exchange_specific_symbols: list[str]) -> None:
    """
    Inserts a row with a crypto id and the corresponding
    supported exchange
    """
    with Session() as session:
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
        except Exception:
            pass
        session.commit()
