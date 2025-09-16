from domain.models import CryptoPairsNames
from services.db_session import Session
from sqlalchemy.dialects.postgresql import insert as upsert


def insert_or_update_pairs(pairs: list[str]) -> None:
    db_readable_dict = [{"crypto_name": pair} for pair in pairs]
    with Session() as session:
        stmt = upsert(CryptoPairsNames).values([*db_readable_dict])
        session.execute(stmt)
        session.commit()
