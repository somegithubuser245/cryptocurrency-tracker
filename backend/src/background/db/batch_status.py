from domain.models import BatchStatus
from services.db_session import DBSessionDep
from sqlalchemy import insert, update


def init_batch_status(
    session: DBSessionDep,
    crypto_ids: list[int],
    interval: str,
) -> None:
    db_readable_dict = [{
        "id": id,
        "interval": interval,
        "saved_cache": False,
        "difference_found": False,
        "saved_db": False
    } for id in crypto_ids]
    stmt = insert(BatchStatus).values(db_readable_dict)
    session.execute(stmt)
    session.commit()

def update_batch_status_cached(
    session: DBSessionDep,
    crypto_ids: list[int],
) -> None:
    """
    Update status fields

    Provide kwargs accordingly to the db schema.

    Example: {"saved_cache": True}

    Or: {"saved_cache": False, "saved_db": True}
    """
    # db_readable_dict = [{"saved_cache": True} for _ in range(len(crypto_ids))]
    stmt = (
        update(BatchStatus)
        .where(BatchStatus.id.in_(crypto_ids))
        .values({"saved_cache": True})
    )
    session.execute(stmt)
    session.commit()