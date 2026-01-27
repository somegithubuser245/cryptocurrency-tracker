import json

from background.celery.celery_conf import scan_app
from background.db.celery import (
    get_ce_ids_by_crypto_id,
    save_compute_mark_complete,
    scan_available_ohlc,
)
from celery import chain, group
from celery.utils.log import get_task_logger
from data_manipulation.spread_object import Spread
from data_manipulation.timeframes_equalizer import TimeframeSynchronizer
from services.db_session import get_session_raw
from utils.dependencies.dependencies import get_redis_client

logger = get_task_logger(__name__)


def run_chunk_compute(ce_ids: list[int]) -> None:
    main_process = chain(get_cached_pairs_list.s(ce_ids), spawn_chunk_computes.s())
    main_process.apply_async()


@scan_app.task
def get_cached_pairs_list(dtos_ids: list[int]) -> list[int]:
    with get_session_raw() as session:
        # get list grouped by ohlc with same crypto name
        return scan_available_ohlc(session=session, dtos_ids=dtos_ids)


@scan_app.task
def spawn_chunk_computes(crypto_ids: list[int]):
    spread_grouped = group(compute_cross_exchange_spread.s(crypto_id) for crypto_id in crypto_ids)
    return spread_grouped.apply_async()


@scan_app.task
def compute_cross_exchange_spread(crypto_id: int) -> None:
    """
    Heavy and hacky method

    Many things happen, and i'm not sure how to
    best refactor / optimize it

    Currently doesn't save computed result, only logs it
    """
    redis_client = get_redis_client()

    ohlc_raw_grouped = []

    with get_session_raw() as session:
        crypto_exchange_ids = get_ce_ids_by_crypto_id(session=session, crypto_id=crypto_id)

    for ce_id in crypto_exchange_ids:
        redis_key = f"OHLC:{ce_id}"
        ohlc_raw = redis_client.get(redis_key)

        # check if data is corrupted at any step
        # shouldn't hapend, but better double check
        if not ohlc_raw or not (serialized := json.loads(ohlc_raw)):
            continue

        ohlc_raw_grouped.append(serialized)

    dataframes_grouped = TimeframeSynchronizer().sync_many(ohlc_raw_grouped)
    spread_obj = Spread(raw_frames=dataframes_grouped, ce_ids=crypto_exchange_ids)

    with get_session_raw() as session:
        save_compute_mark_complete(
            session=session, crypto_id=crypto_id, computed_spread=spread_obj.get_max_spread()
        )
