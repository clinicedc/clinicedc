from collections import OrderedDict
from datetime import datetime
from dateutil.relativedelta import relativedelta

import arrow
from django.apps import apps as django_apps
from edc_base.utils import get_utcnow

from .holidays import Holidays


class Facility:

    holiday_cls = Holidays

    def __init__(self, name=None, days=None, slots=None, forward_only=None):
        self.name = name
        self.days = days
        self.slots = slots or [99999 for _ in self.days]
        self.forward_only = True if forward_only is None else forward_only
        self.config = OrderedDict(zip([str(d) for d in self.days], self.slots))

    def __str__(self):
        return '{} {}'.format(
            self.name.title(),
            ', '.join([str(day) + '(' + str(slot) + ' slots)' for day, slot in self.config.items()]))

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
        """Returns timezone-aware datetime as a UTC arrow object."""
        return arrow.Arrow.fromdatetime(dt, dt.tzinfo).to('utc')

    def not_holiday(self, r):
        """Returns the arrow object, r,  of a suggested calendar date if not a holiday."""
        app_config = django_apps.get_app_config('edc_appointment')
        if not app_config.file_holidays:
            Holiday = django_apps.get_model(
                *'edc_appointment.holiday'.split('.'))
            holidays = [
                obj.day for obj in Holiday.objects.all().order_by('day')]
            if r.date() not in holidays:
                return r
        else:
            if not self.holiday_cls().is_holiday(utc_datetime=r):
                return r
        return None

    def available_datetime(self, suggested_datetime=None, window_delta=None, taken_datetimes=None):
        """Returns a datetime closest to the suggested datetime based on the configuration of the facility.

        To exclude datetimes other than holidays, pass a list of datetimes to `taken_datetimes`."""
        if suggested_datetime:
            rdate = arrow.Arrow.fromdatetime(suggested_datetime)
        else:
            rdate = arrow.Arrow.fromdatetime(get_utcnow())
        if not window_delta:
            window_delta = relativedelta(months=1)
        taken = [self.to_arrow_utc(dt) for dt in taken_datetimes or []]
        maximum = self.to_arrow_utc(rdate.datetime + window_delta)
        for r in arrow.Arrow.span_range('day', rdate.datetime, maximum.datetime):
            # add back time to arrow object, r
            r = arrow.Arrow.fromdatetime(
                datetime.combine(r[0].date(), rdate.time()))
            # see if available
            if r.datetime.weekday() in self.weekdays and (rdate.date() <= r.date() < maximum.date()):
                if (self.not_holiday(r) and r.date() not in [d.date() for d in taken] and
                        self.open_slot_on(r)):
                    return r.datetime
        return rdate.datetime
