from datetime import date, datetime
from zoneinfo import ZoneInfo


class EdcDatetimeError(Exception):
    pass


def get_utcnow() -> datetime:
    return datetime.now().astimezone(ZoneInfo("UTC"))


def get_utcnow_as_date() -> date:
    return datetime.now().astimezone(ZoneInfo("UTC")).date()


def to_utc(dt: datetime) -> datetime:
    """Returns UTC datetime from any aware datetime."""
    return dt.astimezone(ZoneInfo("UTC"))
