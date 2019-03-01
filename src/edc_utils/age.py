import arrow

from dateutil.relativedelta import relativedelta

from .date import get_utcnow, to_arrow_utc, MyTimezone


class AgeValueError(Exception):
    pass


class AgeFormatError(Exception):
    pass


def get_dob(age_in_years, now=None):
    """Returns a DoB for the given age relative to now.

    Used in tests.
    """
    now = now or get_utcnow()
    try:
        now = now.date()
    except AttributeError:
        pass
    return now - relativedelta(years=age_in_years)


def age(born=None, reference_dt=None, timezone=None):
    """Returns a relative delta.

    Convert dates or datetimes to UTC datetimes.
    """
    born_utc = to_arrow_utc(born, timezone)
    reference_dt_utc = to_arrow_utc(reference_dt, timezone)
    rdelta = relativedelta(reference_dt_utc.datetime, born_utc.datetime)
    if born_utc.datetime > reference_dt_utc.datetime:
        raise AgeValueError(
            f"Reference date {reference_dt} {str(reference_dt.tzinfo)} "
            f"precedes DOB {born} {timezone}. Got {rdelta}"
        )
    return rdelta


def formatted_age(born, reference_dt=None, timezone=None):
    formatted_age = "?"
    if born:
        tzinfo = MyTimezone(timezone).tzinfo
        born = arrow.Arrow.fromdate(born, tzinfo=tzinfo).datetime
        reference_dt = reference_dt or get_utcnow()
        age_delta = age(born, reference_dt or get_utcnow())
        if age_delta.years == 0 and age_delta.months <= 0:
            formatted_age = f"{age_delta.days}d"
        elif age_delta.years == 0 and age_delta.months > 0 and age_delta.months <= 2:
            formatted_age = f"{age_delta.months}m{age_delta.days}d"
        elif age_delta.years == 0 and age_delta.months > 2:
            formatted_age = f"{age_delta.months}m"
        elif age_delta.years == 1:
            m = age_delta.months + 12
            formatted_age = f"{m}m"
        else:
            formatted_age = f"{age_delta.years}y"
    return formatted_age


def get_age_in_days(reference_datetime, dob):
    age_delta = age(dob, reference_datetime)
    return age_delta.days
