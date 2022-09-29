from datetime import datetime
from math import ceil
from typing import Any, Optional
from uuid import uuid4
from zoneinfo import ZoneInfo

from .age import AgeValueError, age, formatted_age, get_age_in_days, get_dob
from .date import ceil_secs, floor_secs, get_utcnow, get_utcnow_as_date, to_utc
from .disable_signals import DisableSignals
from .get_static_file import get_static_file
from .show_urls import show_url_names, show_urls
from .text import (
    convert_from_camel,
    convert_php_dateformat,
    formatted_date,
    formatted_datetime,
    get_safe_random_string,
    safe_allowed_chars,
)


def get_uuid():
    return uuid4().hex


def round_up(value: Any, digits: int):
    return ceil(value * (10**digits)) / (10**digits)


def get_datetime_from_env(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    second: int,
    time_zone: str,
    closing_date: Optional[datetime.date] = None,
) -> datetime:
    if closing_date:
        hour = hour or 23
        minute = minute or 59
        second = second or 59
    else:
        hour = hour or 0
        minute = minute or 0
        second = second or 0
    return datetime(
        int(year),
        int(month),
        int(day),
        int(hour),
        int(minute),
        int(second),
        0,
        ZoneInfo(time_zone),
    )
