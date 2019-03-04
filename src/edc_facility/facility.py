import arrow

from collections import OrderedDict
from datetime import datetime
from dateutil.relativedelta import relativedelta, weekday
from django.conf import settings
from edc_utils import get_utcnow, convert_php_dateformat

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
        self,
        name=None,
        days=None,
        slots=None,
        best_effort_available_datetime=None,
        **kwargs,
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
        self.holidays = self.holiday_cls(facility_name=self.name, **kwargs)
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

    def open_slot_on(self, r):
        return True

    def to_arrow_utc(self, dt):
        """Returns timezone-aware datetime as a UTC arrow object.
        """
        return arrow.Arrow.fromdatetime(dt, dt.tzinfo).to("utc")

    def is_holiday(self, arr_utc=None):
        """Returns the arrow object, arr_utc, of a suggested
        calendar date if not a holiday.
        """
        return self.holidays.is_holiday(utc_datetime=arr_utc.datetime)

    def available_datetime(self, **kwargs):
        return self.available_rdate(**kwargs).datetime

    def available_rdate(
        self,
        suggested_datetime=None,
        forward_delta=None,
        reverse_delta=None,
        taken_datetimes=None,
        include_holidays=None,
    ):
        """Returns an arrow object for a datetime equal to or
        close to the suggested datetime.

        To exclude datetimes other than holidays, pass a list of
        datetimes in UTC to `taken_datetimes`.
        """
        available_rdate = None
        forward_delta = forward_delta or relativedelta(months=1)
        reverse_delta = reverse_delta or relativedelta(months=0)
        if suggested_datetime:
            suggested_rdate = arrow.Arrow.fromdatetime(suggested_datetime)
        else:
            suggested_rdate = arrow.Arrow.fromdatetime(get_utcnow())
        minimum = self.to_arrow_utc(suggested_rdate.datetime - reverse_delta)
        maximum = self.to_arrow_utc(suggested_rdate.datetime + forward_delta)
        rtaken = [self.to_arrow_utc(dt) for dt in taken_datetimes or []]
        for r in arrow.Arrow.span_range("day", minimum.datetime, maximum.datetime):
            # add back time to arrow object, r
            r = arrow.Arrow.fromdatetime(
                datetime.combine(r[0].date(), suggested_rdate.time())
            )
            if r.datetime.weekday() in self.weekdays and (
                minimum.date() <= r.date() < maximum.date()
            ):
                if include_holidays:
                    is_holiday = False
                else:
                    is_holiday = self.is_holiday(r)
                if (
                    not is_holiday
                    and r.date() not in [r.date() for r in rtaken]
                    and self.open_slot_on(r)
                ):
                    available_rdate = r
                    break
        if not available_rdate:
            if self.best_effort_available_datetime:
                available_rdate = r
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
        return available_rdate
