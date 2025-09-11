from __future__ import annotations

from datetime import date, datetime
from zoneinfo import ZoneInfo

from dateutil.relativedelta import relativedelta
from django.conf import settings

from .date import get_utcnow


class AgeValueError(Exception):
    pass


class AgeFormatError(Exception):
    pass


def get_dob(age_in_years: int, now: date | datetime | None = None) -> date:
    """Returns a DoB for the given age relative to now.

    Used in tests.
    """
    now = now or get_utcnow()
    try:
        now = now.date()
    except AttributeError:
        pass
    return now - relativedelta(years=age_in_years)


def age(
    born: date | datetime,
    reference_dt: date | datetime,
    timezone: str | None = None,
) -> relativedelta:
    """Returns a relative delta.

    Convert dates or datetimes to UTC datetimes.
    """
    if born is None:
        raise AgeValueError("DOB cannot be None")
    try:
        born_utc = born.astimezone(ZoneInfo("UTC"))
    except AttributeError:
        born_utc = datetime(*[*born.timetuple()][0:6], tzinfo=ZoneInfo("UTC"))
    try:
        reference_dt_utc = reference_dt.astimezone(ZoneInfo("UTC"))
    except AttributeError:
        reference_dt_utc = datetime(*[*reference_dt.timetuple()][0:6], tzinfo=ZoneInfo("UTC"))
    rdelta = relativedelta(reference_dt_utc, born_utc)
    if born_utc > reference_dt_utc:
        raise AgeValueError(
            f"Reference date {reference_dt} {str(reference_dt.tzinfo)} "
            f"precedes DOB {born} {timezone}. Got {rdelta}"
        )
    return rdelta


def formatted_age(
    born: date | datetime | None,
    reference_dt: date | datetime,
    timezone: str | None = None,
) -> str:
    age_as_str = "?"
    if born:
        timezone = timezone or getattr(settings, "TIME_ZONE", "UTC")
        born = datetime(*[*born.timetuple()][0:6], tzinfo=ZoneInfo(timezone))
        reference_dt = reference_dt or get_utcnow()
        age_delta = age(born, reference_dt or get_utcnow())
        if age_delta.years == 0 and age_delta.months <= 0:
            age_as_str = f"{age_delta.days}d"
        elif age_delta.years == 0 and 0 < age_delta.months <= 2:
            age_as_str = f"{age_delta.months}m{age_delta.days}d"
        elif age_delta.years == 0 and age_delta.months > 2:
            age_as_str = f"{age_delta.months}m"
        elif age_delta.years == 1:
            m = age_delta.months + 12
            age_as_str = f"{m}m"
        else:
            age_as_str = f"{age_delta.years}y"
    return age_as_str


def get_age_in_days(reference_datetime: date | datetime, dob: date | datetime) -> int:
    age_delta = age(dob, reference_datetime)
    return age_delta.days
