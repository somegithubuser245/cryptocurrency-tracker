from datetime import datetime
from zoneinfo import ZoneInfo

from config.config import LocalTimeZone

try:
    LOCAL_TZ = ZoneInfo(LocalTimeZone().TIMEZONE)
except Exception:
    # if .astimezone() is given a None value,
    # it will use system default timezone
    LOCAL_TZ = None


def normalize_timestamp(value: datetime) -> datetime:
    return value.astimezone(tz=LOCAL_TZ)
