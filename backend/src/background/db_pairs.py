from domain.models import CryptoPairName, SupportedExchangesByCrypto
from services.db_session import Session
from sqlalchemy import insert
from sqlalchemy.dialects.postgresql import insert as upsert


def insert_or_update_pairs(pairs: list[str]) -> list[int]:
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
