import arrow

from dateutil.relativedelta import relativedelta

from .date import get_utcnow, to_arrow_utc, MyTimezone


class AgeValueError(Exception):
    pass


def get_dob(age_in_years, now=None):
    """Returns a DoB for the given age relative to now.

    Meant for tests.
    """
    if now:
        try:
            now = now.date()
        except AttributeError:
            pass
    now = now or get_utcnow().date()
    return now - relativedelta(years=age_in_years)


def age(born, reference_dt, timezone=None):
    """Returns a relative delta"""
    # avoid null dates/datetimes
    if not born:
        raise AgeValueError("Date of birth is required.")
    if not reference_dt:
        raise AgeValueError("Reference date is required.")
    # convert dates or datetimes to UTC datetimes
    born_utc = to_arrow_utc(born, timezone)
    reference_dt_utc = to_arrow_utc(reference_dt, timezone)
    rdelta = relativedelta(reference_dt_utc.datetime, born_utc.datetime)
    if born_utc.datetime > reference_dt_utc.datetime:
        raise AgeValueError(
            "Reference date {} {} precedes DOB {} {}. Got {}".format(
                reference_dt, str(reference_dt.tzinfo), born, timezone, rdelta
            )
        )
    return rdelta


def formatted_age(born, reference_dt=None, timezone=None):
    if born:
        tzinfo = MyTimezone(timezone).tzinfo
        born = arrow.Arrow.fromdate(born, tzinfo=tzinfo).datetime
        reference_dt = reference_dt or get_utcnow()
        age_delta = age(born, reference_dt or get_utcnow())
        if born > reference_dt:
            return "?"
        elif age_delta.years == 0 and age_delta.months <= 0:
            return "%sd" % (age_delta.days)
        elif age_delta.years == 0 and age_delta.months > 0 and age_delta.months <= 2:
            return "%sm%sd" % (age_delta.months, age_delta.days)
        elif age_delta.years == 0 and age_delta.months > 2:
            return "%sm" % (age_delta.months)
        elif age_delta.years == 1:
            m = age_delta.months + 12
            return "%sm" % (m)
        elif age_delta.years > 1:
            return "%sy" % (age_delta.years)
        else:
            raise TypeError(
                "Age template tag missed a case... today - born. "
                "rdelta = {} and {}".format(age_delta, born)
            )


def get_age_in_days(reference_datetime, dob):
    age_delta = age(dob, reference_datetime)
    return age_delta.days
