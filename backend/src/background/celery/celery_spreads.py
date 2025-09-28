import json

from celery import chain, group
from background.celery.celery_conf import scan_app
from background.db.celery import get_ce_ids_by_crypto_id, get_exchange_name_by_id, scan_available_ohlc
from data_manipulation.spread_object import Spread
from data_manipulation.timeframes_equalizer import TimeframeSynchronizer
from services.caching import RedisClient
from services.db_session import get_session_raw

from celery.utils.log import get_task_logger

from utils.dependencies.dependencies import get_redis_client

logger = get_task_logger(__name__)


def run_chunk_compute(ce_ids: list[int]):
    main_process = chain(get_cached_pairs_list.s(ce_ids), spawn_chunk_computes.s())
    main_process.apply_async()


@scan_app.task
def get_cached_pairs_list(dtos_ids: list[int]):
    session = get_session_raw()

    # get list grouped by ohlc with same crypto name
    return scan_available_ohlc(session=session, dtos_ids=dtos_ids)

@scan_app.task
def spawn_chunk_computes(crypto_ids: list[int]):
    spread_grouped = group(compute_cross_exchange_spread.s(
        crypto_id
    ) for crypto_id in crypto_ids)
    return spread_grouped.apply_async()

@scan_app.task
def compute_cross_exchange_spread(crypto_id: int):
    """
    Heavy and hacky method

    Many things happen, and i'm not sure how to 
    best refactor / optimize it

    Currently doesn't save computed result, only logs it
    """
    session = get_session_raw()
    redis_client = get_redis_client()

    ohlc_raw_grouped = []
    
    crypto_exchange_ids = get_ce_ids_by_crypto_id(
        session=session, crypto_id=crypto_id
    )
    for ce_id in crypto_exchange_ids:
        redis_key = f"OHLC:{ce_id}"
        ohlc_raw = redis_client.get(redis_key)

        # check if data is corrupted at any step
        # shouldn't hapend, but better double check
        if not ohlc_raw or not (serialized := json.loads(ohlc_raw)):
            continue

        ohlc_raw_grouped.append(serialized)

    session.close()

    timestamp_syncer = TimeframeSynchronizer()
    
    dataframes_grouped = timestamp_syncer.sync_many(ohlc_raw_grouped)
    spread_obj = Spread(
        raw_frames=dataframes_grouped,
        ce_ids=crypto_exchange_ids,
    )
    msg = f"SPREAD FOR {crypto_id}: {str(spread_obj.get_max_spread())}"
    logger.info(msg)
    return spread_obj.get_max_spread()

        
@scan_app.task
def scan_through_and_validate(dtos_ids: list[int]):
    """
    Scans through the db and validates if dtos in-memory
    have been initialized in the db
    """
    session = get_session_raw()
    length_db = len(scan_available_ohlc(session, dtos_ids=dtos_ids))
    session.close()
    length_dtos = len(dtos_ids)

    logger.info(f"CELERY EXEC: \t{length_db}-db  \t{length_dtos}--dto")
    return length_db == length_dtos
