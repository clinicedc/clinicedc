import arrow

from arrow.arrow import Arrow
from dateutil import tz

try:
    from django.conf import settings
except ImportError:
    TIME_ZONE = "UTC"
else:
    TIME_ZONE = settings.TIME_ZONE


class MyTimezone:
    def __init__(self, timezone):
        if timezone:
            self.tzinfo = tz.gettz(timezone)
        else:
            self.tzinfo = tz.gettz(TIME_ZONE)


def get_utcnow():
    return arrow.utcnow().datetime


def to_arrow_utc(dt, timezone=None):
    """Returns a datetime after converting date or datetime from
    the given timezone string to \'UTC\'.
    """
    try:
        dt.date()
    except AttributeError:
        # handle born as date. Use 0hr as time before converting to UTC
        tzinfo = MyTimezone(timezone).tzinfo
        r_utc = arrow.Arrow.fromdate(dt, tzinfo=tzinfo).to("utc")
    else:
        # handle born as datetime
        r_utc = arrow.Arrow.fromdatetime(dt, tzinfo=dt.tzinfo).to("utc")
    return r_utc


def to_utc(dt):
    """Returns UTC datetime from any aware datetime.
    """
    return Arrow.fromdatetime(dt, dt.tzinfo).to("utc").datetime
