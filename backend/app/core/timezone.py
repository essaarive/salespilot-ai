import os
import warnings
from datetime import datetime, time, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

DEFAULT_APP_TIMEZONE = "Asia/Shanghai"


def get_app_timezone() -> ZoneInfo:
    timezone_name = os.getenv("APP_TIMEZONE") or DEFAULT_APP_TIMEZONE
    try:
        return ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError:
        warnings.warn(
            f"Invalid APP_TIMEZONE={timezone_name!r}; fallback to {DEFAULT_APP_TIMEZONE}.",
            RuntimeWarning,
            stacklevel=2,
        )
        return ZoneInfo(DEFAULT_APP_TIMEZONE)


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def now_utc_naive() -> datetime:
    """SQLite stores naive datetimes in this MVP; treat them as UTC."""
    return now_utc().replace(tzinfo=None)


def now_local() -> datetime:
    return now_utc().astimezone(get_app_timezone())


def ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def format_datetime(value: datetime) -> str:
    return ensure_utc(value).isoformat()


def local_day_bounds_utc_naive() -> tuple[datetime, datetime]:
    local_tz = get_app_timezone()
    today = now_local().date()
    start = datetime.combine(today, time.min, local_tz).astimezone(timezone.utc).replace(tzinfo=None)
    end = datetime.combine(today, time.max, local_tz).astimezone(timezone.utc).replace(tzinfo=None)
    return start, end
