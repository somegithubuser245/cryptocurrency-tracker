from celery import Celery
from config.config import RedisSettings

redis_url = RedisSettings().construct_celery_url()

scan_app = Celery("db_scanner",
                  broker=redis_url,
                  backend=redis_url,
                  include=["background.celery.celery_spreads"])