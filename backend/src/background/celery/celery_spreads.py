from background.celery.celery_conf import scan_app
from background.db.celery import scan_available_ohlc
from services.db_session import get_session_as_is

from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@scan_app.task
def scan_through_and_validate(dtos_ids: list[int]):
    """
    Scans through the db and validates if dtos in-memory
    have been initialized in the db
    """
    session = get_session_as_is()
    length_db = len(scan_available_ohlc(session, dtos_ids=dtos_ids))
    length_dtos = len(dtos_ids)

    logger.info(f"CELERY EXEC: \t{length_db}-db  \t{length_dtos}--dto")
    return length_db == length_dtos
        
