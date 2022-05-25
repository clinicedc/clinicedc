from datetime import date, datetime
from typing import Optional
from zoneinfo import ZoneInfo

import arrow
from arrow.arrow import Arrow


class EdcDatetimeError(Exception):
    pass


def get_utcnow() -> datetime:
    return arrow.utcnow().datetime


def get_utcnow_as_date() -> date:
    return arrow.utcnow().date()


def to_arrow_utc(dt: datetime, timezone: Optional[str] = None):
    """Returns an arrow instance in UTC after converting date or datetime from
    the given timezone string to \'UTC\'.
    """
    try:
        dt.date()
    except AttributeError:
        # handle born as date. Use 0hr as time before converting to UTC
        r_utc = arrow.Arrow.fromdate(dt, tzinfo=ZoneInfo("UTC"))
    else:
        if timezone:
            raise EdcDatetimeError("Timezone param not expected if dt is a datetime.")
        # handle born as datetime
        r_utc = arrow.Arrow.fromdatetime(dt, tzinfo=dt.tzinfo).to("utc")
    return r_utc


def to_utc(dt: datetime) -> datetime:
    """Returns UTC datetime from any aware datetime."""
    return Arrow.fromdatetime(dt, dt.tzinfo).to("utc").datetime
