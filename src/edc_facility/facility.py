import arrow

from collections import OrderedDict
from datetime import datetime
from dateutil.relativedelta import relativedelta
from dateutil._common import weekday
from django.conf import settings
from edc_utils import get_utcnow, convert_php_dateformat
from operator import methodcaller

from .holidays import Holidays


class FacilityError(Exception):
    pass


class Facility:

    """
    Note: `best_effort_available_datetime` (Default: False) if True
        will set available_rdata to the suggested_datetime if no
        available_rdata can be found. This is not ideal and could
        lead to a protocol violation but may be helpful for facilities
        open 1 or 2 days per week where the visit has a very
        narrow window period (forward_delta, reverse_delta).
    """

    holiday_cls = Holidays

    def __init__(
        self, name=None, days=None, slots=None, best_effort_available_datetime=None,
    ):
        self.days = []
        self.name = name
        for day in days:
            try:
                day.weekday
            except AttributeError:
                day = weekday(day)
            self.days.append(day)
        self.slots = slots or [99999 for _ in self.days]
        self.config = OrderedDict(zip([str(d) for d in self.days], self.slots))
        self.holidays = self.holiday_cls()
        if not name:
            raise FacilityError(f"Name cannot be None. See {repr(self)}")
        self.best_effort_available_datetime = (
            True
            if best_effort_available_datetime is None
            else best_effort_available_datetime
        )

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name}, days={self.days})"

    def __str__(self):
        description = ", ".join(
            [
                str(day) + "(" + str(slot) + " slots)"
                for day, slot in self.config.items()
            ]
        )
        return f"{self.name.title()} {description}"

    def slots_per_day(self, day):
        try:
            slots_per_day = self.config.get(str(day))
        except KeyError:
            slots_per_day = 0
        return slots_per_day

    @property
    def weekdays(self):
        return [d.weekday for d in self.days]

    @staticmethod
    def open_slot_on(arw):
        """Hook for handling load balance by day.

        For example, if 15 appointment `slots` are filled out of 30
        allowed for Monday, return arw, if 30/30 return None.
        """
        return arw

    @staticmethod
    def to_arrow_utc(dt):
        """Returns timezone-aware datetime as a UTC arrow object.
        """
        return arrow.Arrow.fromdatetime(dt, dt.tzinfo).to("utc")

    def is_holiday(self, arr_utc=None):
        """Returns the arrow object, arr_utc, of a suggested
        calendar date if not a holiday.
        """
        return self.holidays.is_holiday(utc_datetime=arr_utc.datetime)

    def available_datetime(self, **kwargs):
        return self.available_arw(**kwargs).datetime

    def get_arw_span(self, suggested_arw, forward_delta, reverse_delta):
        """Returns a list of arrow objects in a custom ordered.
         Objects are ordered around the suggested date. For example,

         """
        min_arw = self.to_arrow_utc(suggested_arw.datetime - reverse_delta)
        max_arw = self.to_arrow_utc(suggested_arw.datetime + forward_delta)
        span = [
            arw[0]
            for arw in arrow.Arrow.span_range("day", min_arw.datetime, max_arw.datetime)
        ]
        span_lt = [arw for arw in span if arw.date() < suggested_arw.date()]
        span_lt = sorted(span_lt, key=methodcaller("date"), reverse=True)
        span_gt = [arw for arw in span if arw.date() > suggested_arw.date()]
        arw_span = []
        max_len = len(span_gt) if len(span_gt) > len(span_lt) else len(span_lt)
        for i in range(0, max_len):
            try:
                item = span_lt.pop()
            except IndexError:
                pass
            else:
                arw_span.insert(0, item)
            try:
                item = span_gt.pop()
            except IndexError:
                pass
            else:
                arw_span.insert(0, item)
        arw_span.insert(0, suggested_arw)
        return arw_span, min_arw, max_arw

    def available_arw(
        self,
        suggested_datetime=None,
        forward_delta=None,
        reverse_delta=None,
        taken_datetimes=None,
        schedule_on_holidays=None,
    ):
        """Returns an arrow object for a datetime equal to or
        close to the suggested datetime.

        To exclude datetimes other than holidays, pass a list of
        datetimes in UTC to `taken_datetimes`.
        """
        available_arw = None
        forward_delta = forward_delta or relativedelta(months=1)
        reverse_delta = reverse_delta or relativedelta(months=0)
        taken_arw = [self.to_arrow_utc(dt) for dt in taken_datetimes or []]
        if suggested_datetime:
            suggested_arw = arrow.Arrow.fromdatetime(suggested_datetime)
        else:
            suggested_arw = arrow.Arrow.fromdatetime(get_utcnow())
        arw_span_range, min_arw, max_arw = self.get_arw_span(
            suggested_arw, forward_delta, reverse_delta,
        )
        for arw in arw_span_range:
            # add back time to arrow object, r
            if arw.date().weekday() in self.weekdays and (
                min_arw.date() <= arw.date() < max_arw.date()
            ):
                is_holiday = False if schedule_on_holidays else self.is_holiday(arw)
                if (
                    not is_holiday
                    and arw.date() not in [a.date() for a in taken_arw]
                    and self.open_slot_on(arw)
                ):
                    available_arw = arw
                    break
        if not available_arw:
            if self.best_effort_available_datetime:
                available_arw = suggested_arw
            else:
                formatted_date = suggested_datetime.strftime(
                    convert_php_dateformat(settings.SHORT_DATE_FORMAT)
                )
                raise FacilityError(
                    f"No available appointment dates at facility for period. "
                    f"Got no available dates within {reverse_delta.days}-"
                    f"{forward_delta.days} days of {formatted_date}. "
                    f"Facility is {repr(self)}."
                )
        available_arw = arrow.Arrow.fromdatetime(
            datetime.combine(available_arw.date(), suggested_arw.time())
        )
        return available_arw
