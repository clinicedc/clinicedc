from __future__ import annotations

from datetime import date, datetime
from zoneinfo import ZoneInfo

from django.conf import settings


class EdcDatetimeError(Exception):
    pass


def get_utcnow() -> datetime:
    return datetime.now().astimezone(ZoneInfo("UTC"))


def get_utcnow_as_date() -> date:
    return datetime.now().astimezone(ZoneInfo("UTC")).date()


def to_utc(dt: datetime) -> datetime:
    """Returns UTC datetime from any aware datetime."""
    return dt.astimezone(ZoneInfo("UTC"))


def to_local(dt: datetime) -> datetime:
    """Returns local datetime from any aware datetime."""
    return dt.astimezone(ZoneInfo(settings.TIME_ZONE))


def floor_secs(dte) -> datetime:
    return datetime(dte.year, dte.month, dte.day, dte.hour, dte.minute, 0, 0).astimezone(
        dte.tzinfo
    )


def ceil_secs(dte) -> datetime:
    return datetime(dte.year, dte.month, dte.day, dte.hour, dte.minute, 59, 999999).astimezone(
        dte.tzinfo
    )


def floor_datetime(dt) -> datetime:
    return dt.replace(hour=0, minute=0, second=0, microsecond=0).astimezone(ZoneInfo("UTC"))


def ceil_datetime(dt) -> datetime:
    return dt.replace(hour=23, minute=59, second=59, microsecond=999999).astimezone(
        ZoneInfo("UTC")
    )
