import arrow
import pytz
from arrow.arrow import Arrow
from django.conf import settings


class EdcDatetimeError(Exception):
    pass


def get_utcnow():
    return arrow.utcnow().datetime


def to_arrow_utc(dt, timezone=None):
    """Returns a datetime in UTC after converting date or datetime from
    the given timezone string to \'UTC\'.
    """
    try:
        dt.date()
    except AttributeError:
        # handle born as date. Use 0hr as time before converting to UTC
        timezone = timezone or getattr(settings, "TIME_ZONE", "UTC")
        r_utc = arrow.Arrow.fromdate(dt, tzinfo=pytz.timezone(timezone)).to("utc")
    else:
        if timezone:
            raise EdcDatetimeError("Timezone param not expected if dt is a datetime.")
        # handle born as datetime
        r_utc = arrow.Arrow.fromdatetime(dt, tzinfo=dt.tzinfo).to("utc")
    return r_utc


def to_utc(dt):
    """Returns UTC datetime from any aware datetime."""
    return Arrow.fromdatetime(dt, dt.tzinfo).to("utc").datetime
