import json

from celery import chain, group
from background.celery.celery_conf import scan_app
from background.db.celery import get_exchange_name_by_id, scan_available_ohlc
from data_manipulation.spread_object import Spread
from data_manipulation.timeframes_equalizer import TimeframeSynchronizer
from services.caching import RedisClient
from services.db_session import get_session_raw

from celery.utils.log import get_task_logger

from utils.dependencies.dependencies import get_redis_client

logger = get_task_logger(__name__)

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

def run_chunk_compute(dtos_ids: list[int]):
    main_process = chain(get_cached_pairs_list.s(dtos_ids), spawn_chunk_computes.s())
    main_process.apply_async()


@scan_app.task
def get_cached_pairs_list(dtos_ids: list[int]):
    session = get_session_raw()

    # get list grouped by ohlc with same crypto name
    return scan_available_ohlc(session=session, dtos_ids=dtos_ids)

@scan_app.task
def spawn_chunk_computes(ce_ids_grouped: list[list[int]]):
    spread_grouped = group(compute_cross_exchange_spread.s(
        ce_ids_group
    ) for ce_ids_group in ce_ids_grouped)
    return spread_grouped.apply_async()

@scan_app.task
def compute_cross_exchange_spread(crypto_exchange_ids: list[int]):
    """
    Heavy and hacky method

    Many things happen, and i'm not sure how to 
    best refactor / optimize it

    Currently doesn't save computed result, only logs it
    """
    session = get_session_raw()
    redis_client = get_redis_client()

    ohlc_raw_grouped = []
    exchange_names = []
    for ce_id in crypto_exchange_ids:
        redis_key = f"OHLC:{ce_id}"
        ohlc_raw = redis_client.get(redis_key)

        if not ohlc_raw:
            continue

        serialized = json.loads(ohlc_raw)

        if not serialized:
            continue

        ohlc_raw_grouped.append(serialized)

        exchange_name = get_exchange_name_by_id(session=session, ce_id=ce_id)
        exchange_names.append(exchange_name)

    session.close()

    timestamp_syncer = TimeframeSynchronizer()
    logger.info(exchange_names)
    
    dataframes_grouped = timestamp_syncer.sync_many(ohlc_raw_grouped)
    spread_obj = Spread(
        raw_frames=dataframes_grouped,
        exchange_names=exchange_names,
    )
    msg = f"SPREAD FOR {crypto_exchange_ids[0]}: {str(spread_obj.get_max_spread())}"
    logger.info(msg)

        
