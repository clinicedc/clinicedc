from datetime import date, datetime
from typing import Optional, Union

import arrow
import pytz
from dateutil.relativedelta import relativedelta
from django.conf import settings

from .date import get_utcnow, to_arrow_utc


class AgeValueError(Exception):
    pass


class AgeFormatError(Exception):
    pass


def get_dob(age_in_years, now=None) -> date:
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
    born: Union[date, datetime],
    reference_dt: Union[date, datetime],
    timezone: Optional[str] = None,
) -> relativedelta:
    """Returns a relative delta.

    Convert dates or datetimes to UTC datetimes.
    """
    if born is None:
        raise AgeValueError("DOB cannot be None")
    born_utc = to_arrow_utc(born, timezone)
    reference_dt_utc = to_arrow_utc(reference_dt, timezone)
    rdelta = relativedelta(reference_dt_utc.datetime, born_utc.datetime)
    if born_utc.datetime > reference_dt_utc.datetime:
        raise AgeValueError(
            f"Reference date {reference_dt} {str(reference_dt.tzinfo)} "
            f"precedes DOB {born} {timezone}. Got {rdelta}"
        )
    return rdelta


def formatted_age(
    born: Union[date, datetime],
    reference_dt: Union[date, datetime],
    timezone: Optional[str] = None,
) -> str:
    formatted_age_ = "?"
    if born:
        timezone = timezone or getattr(settings, "TIME_ZONE", "UTC")
        born = arrow.Arrow.fromdate(born, tzinfo=pytz.timezone(timezone)).datetime
        reference_dt = reference_dt or get_utcnow()
        age_delta = age(born, reference_dt or get_utcnow())
        if age_delta.years == 0 and age_delta.months <= 0:
            formatted_age_ = f"{age_delta.days}d"
        elif age_delta.years == 0 and 0 < age_delta.months <= 2:
            formatted_age_ = f"{age_delta.months}m{age_delta.days}d"
        elif age_delta.years == 0 and age_delta.months > 2:
            formatted_age_ = f"{age_delta.months}m"
        elif age_delta.years == 1:
            m = age_delta.months + 12
            formatted_age_ = f"{m}m"
        else:
            formatted_age_ = f"{age_delta.years}y"
    return formatted_age_


def get_age_in_days(
    reference_datetime: Union[date, datetime], dob: Union[date, datetime]
) -> int:
    age_delta = age(dob, reference_datetime)
    return age_delta.days
