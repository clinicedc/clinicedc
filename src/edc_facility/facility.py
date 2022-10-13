from __future__ import annotations

from datetime import datetime
from operator import methodcaller
from typing import Any, List, Tuple, Union
from zoneinfo import ZoneInfo

import arrow
from arrow import Arrow
from dateutil._common import weekday
from dateutil.relativedelta import relativedelta
from django.conf import settings
from edc_utils import convert_php_dateformat, get_utcnow, to_utc

from .exceptions import FacilityError
from .holidays import Holidays


class Facility:

    """
    Note: `best_effort_available_datetime` (Default: False) if True
        will set available_rdata to the suggested_datetime if no
        available_rdata can be found. This is not ideal and could
        lead to a protocol violation but may be helpful for facilities
        open 1 or 2 days per week, where the visit has a very
        narrow window period (forward_delta, reverse_delta).
    """

    holiday_cls = Holidays

    def __init__(
        self,
        name: str = None,
        days: list = None,
        slots: list[int] = None,
        best_effort_available_datetime: datetime | None = None,
    ):
        self.days = []
        self.name = name
        if not name:
            raise FacilityError(f"Name cannot be None. See {repr(self)}")
        self.best_effort_available_datetime = (
            True if best_effort_available_datetime is None else best_effort_available_datetime
        )
        for day in days:
            try:
                day.weekday
            except AttributeError:
                day = weekday(day)
            self.days.append(day)
        self.slots = slots or [99999 for _ in self.days]
        self.config = dict(zip([str(d) for d in self.days], self.slots))
        self.holidays = self.holiday_cls()

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name}, days={self.days})"

    def __str__(self):
        description = ", ".join(
            [str(day) + "(" + str(slot) + " slots)" for day, slot in self.config.items()]
        )
        return f"{self.name.title()} {description}"

    def slots_per_day(self, day) -> int:
        try:
            slots_per_day = self.config.get(str(day))
        except KeyError:
            slots_per_day = 0
        return slots_per_day

    @property
    def weekdays(self) -> list[int]:
        return [d.weekday for d in self.days]

    @staticmethod
    def open_slot_on(arr) -> Arrow:
        """Hook for handling load balance by day.

        For example, if 15 appointment `slots` are filled out of 30
        allowed for Monday, return arw, if 30/30 return None.
        """
        return arr

    def is_holiday(self, dt: datetime) -> bool:
        return self.holidays.is_holiday(utc_datetime=to_utc(dt))

    def available_datetime(self, **kwargs) -> datetime:
        return self.available_arr(**kwargs).datetime

    @staticmethod
    def get_arr_span(
        suggested_arr, forward_delta, reverse_delta
    ) -> Tuple[List[Union[Arrow, Any]], Arrow, Arrow]:
        """Returns a list of arrow objects in a custom ordered.
        Objects are ordered around the suggested date. For example,
        """
        # min_arw = self.to_arrow_utc(suggested_arr.datetime - reverse_delta)
        min_arr = Arrow.fromdate(
            suggested_arr.datetime - reverse_delta, tzinfo=ZoneInfo("UTC")
        )
        # max_arw = self.to_arrow_utc(suggested_arw.datetime + forward_delta)
        max_arr = Arrow.fromdate(
            suggested_arr.datetime + forward_delta, tzinfo=ZoneInfo("UTC")
        )
        span = [arw[0] for arw in Arrow.span_range("day", min_arr.datetime, max_arr.datetime)]
        span_lt = [arw for arw in span if arw.date() < suggested_arr.date()]
        span_lt = sorted(span_lt, key=methodcaller("date"), reverse=True)
        span_gt = [arw for arw in span if arw.date() > suggested_arr.date()]
        arr_span = []
        max_len = len(span_gt) if len(span_gt) > len(span_lt) else len(span_lt)
        for i in range(0, max_len):
            try:
                item = span_lt.pop()
            except IndexError:
                pass
            else:
                arr_span.insert(0, item)
            try:
                item = span_gt.pop()
            except IndexError:
                pass
            else:
                arr_span.insert(0, item)
        arr_span.insert(0, suggested_arr)
        return arr_span, min_arr, max_arr

    def available_arr(
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
        available_arr = None
        forward_delta = forward_delta or relativedelta(months=1)
        reverse_delta = reverse_delta or relativedelta(months=0)
        taken_arr = [
            arrow.Arrow.fromdatetime(dt, tzinfo=ZoneInfo("UTC")).to("utc")
            for dt in taken_datetimes or []
        ]
        if suggested_datetime:
            suggested_arr = arrow.Arrow.fromdatetime(suggested_datetime)
        else:
            suggested_arr = arrow.Arrow.fromdatetime(get_utcnow())
        arr_span_range, min_arr, max_arr = self.get_arr_span(
            suggested_arr,
            forward_delta,
            reverse_delta,
        )
        for arr in arr_span_range:
            # add back time to arrow object, r
            if arr.date().weekday() in self.weekdays and (
                min_arr.date() <= arr.date() < max_arr.date()
            ):
                is_holiday = False if schedule_on_holidays else self.is_holiday(arr.datetime)
                if (
                    not is_holiday
                    and arr.date() not in [a.date() for a in taken_arr]
                    and self.open_slot_on(arr)
                ):
                    available_arr = arr
                    break
        if not available_arr:
            if self.best_effort_available_datetime:
                available_arr = suggested_arr
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
        available_arr = arrow.Arrow.fromdatetime(
            datetime.combine(available_arr.date(), suggested_arr.time())
        )
        return available_arr
