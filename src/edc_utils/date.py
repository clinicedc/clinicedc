from __future__ import annotations

from datetime import date, datetime
from zoneinfo import ZoneInfo

from django.utils import timezone


class EdcDatetimeError(Exception):
    pass


def get_utcnow() -> datetime:
    return timezone.localtime(None, timezone=ZoneInfo("UTC"))


def get_utcnow_as_date() -> date:
    return timezone.localtime(None, timezone=ZoneInfo("UTC")).date()


def to_utc(dte: datetime) -> datetime | None:
    """Returns UTC datetime from any aware datetime."""
    return timezone.localtime(dte, timezone=ZoneInfo("UTC")) if dte else None


def to_local(dte: datetime) -> datetime | None:
    """Returns local datetime from any aware datetime."""
    return timezone.localtime(dte) if dte else None


def floor_secs(dte) -> datetime:
    return datetime(
        dte.year, dte.month, dte.day, dte.hour, dte.minute, 0, 0, tzinfo=dte.tzinfo
    )


def ceil_secs(dte) -> datetime:
    return datetime(
        dte.year,
        dte.month,
        dte.day,
        dte.hour,
        dte.minute,
        59,
        999999,
        tzinfo=dte.tzinfo,
    )


def floor_datetime(dt) -> datetime:
    return dt.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=dt.tzinfo)


def ceil_datetime(dt) -> datetime:
    return dt.replace(hour=23, minute=59, second=59, microsecond=999999, tzinfo=dt.tzinfo)
