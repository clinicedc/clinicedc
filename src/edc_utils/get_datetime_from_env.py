from datetime import date, datetime
from zoneinfo import ZoneInfo


def get_datetime_from_env(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    second: int,
    time_zone: str,
    closing_date: date = None,
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
