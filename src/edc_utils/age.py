from __future__ import annotations

import contextlib
from datetime import date, datetime
from zoneinfo import ZoneInfo

from dateutil.relativedelta import relativedelta
from django.utils import timezone
from multisite.utils import get_multisite_timezone

from edc_utils.text import formatted_datetime


class AgeValueError(Exception):
    pass


class AgeFormatError(Exception):
    pass


TWO_MONTHS = 2
TWELVE_MONTHS = 12


def get_dob(age_in_years: int, now: date | datetime | None = None) -> date:
    """Returns a DoB for the given age relative to now.

    Used in tests.
    """
    now = now or timezone.now()
    with contextlib.suppress(AttributeError):
        now = now.date()
    return now - relativedelta(years=age_in_years)


def _as_aware_datetime(value: date | datetime, tz: ZoneInfo, label: str) -> datetime:
    """Returns `value` as an aware datetime, a `date` becoming midnight.

    A `date` carries no time to be ambiguous about, so it is anchored to
    local midnight. A naive `datetime` is a caller bug: assuming a
    timezone for it would silently shift the result by the offset.

    Note `datetime` subclasses `date`, so test for the narrower type.
    """
    if not isinstance(value, datetime):
        return datetime(value.year, value.month, value.day, tzinfo=tz)
    if timezone.is_naive(value):
        raise AgeValueError(f"{label} must be an aware datetime. Got {value!r}.")
    return value


def age(born: date | datetime, reference_dt: date | datetime) -> relativedelta:
    """Returns the age at `reference_dt` as a relativedelta.

    A `date` is taken as local midnight on that day, so age advances at
    the start of the birthday. A `datetime` keeps its time, which is
    what allows a neonatal age to be reported in hours.

    That distinction is deliberate but easy to trip over: a subject born
    at 14:23 has not yet turned 25 at midnight on their 25th birthday.
    Pass both arguments as the same type unless you intend it. `dob` is
    a DateField, so a value loaded from the db is a `date`, but an
    unsaved instance may still hold the `datetime` it was built with.

    A naive datetime raises AgeValueError.
    """
    if born is None:
        raise AgeValueError("DOB cannot be None")
    if reference_dt is None:
        raise AgeValueError("Reference date cannot be None")

    tz = ZoneInfo(get_multisite_timezone())
    born = _as_aware_datetime(born, tz, "DOB")
    reference_dt = _as_aware_datetime(reference_dt, tz, "Reference date")

    if born > reference_dt:
        raise AgeValueError(
            f"Reference date {formatted_datetime(reference_dt)} precedes DOB "
            f"{formatted_datetime(born)}."
        )
    return relativedelta(reference_dt, born)


def formatted_age(
    born: date | datetime | None,
    reference_dt: date | datetime,
    tz: str | None = None,
) -> str:
    age_as_str = "?"
    if born:
        tz = tz or get_multisite_timezone()
        born = datetime(*[*born.timetuple()][0:6], tzinfo=ZoneInfo(tz))
        reference_dt = reference_dt or timezone.now()
        age_delta = age(born, reference_dt or timezone.now())
        if age_delta.years == 0 and age_delta.months <= 0:
            age_as_str = f"{age_delta.days}d"
        elif age_delta.years == 0 and 0 < age_delta.months <= TWO_MONTHS:
            age_as_str = f"{age_delta.months}m{age_delta.days}d"
        elif age_delta.years == 0 and age_delta.months > TWO_MONTHS:
            age_as_str = f"{age_delta.months}m"
        elif age_delta.years == 1:
            m = age_delta.months + TWELVE_MONTHS
            age_as_str = f"{m}m"
        else:
            age_as_str = f"{age_delta.years}y"
    return age_as_str


def get_age_in_days(reference_datetime: date | datetime, dob: date | datetime) -> int:
    age_delta = age(dob, reference_datetime)
    return age_delta.days
