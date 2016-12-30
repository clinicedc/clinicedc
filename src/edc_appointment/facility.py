import arrow

from django.apps import apps as django_apps
from datetime import datetime
from collections import OrderedDict
from calendar import Calendar
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, MONTHLY


class Facility:
    def __init__(self, name, days, slots, forward_only=None):
        self.name = name
        self.days = days
        self.slots = slots
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

    def as_arrow_utc(self, dt):
        """Returns timezone-aware datetime as a UTC arrow object."""
        return arrow.Arrow.fromdatetime(dt, dt.tzinfo).to('utc')

    def not_holiday(self, r):
        """Returns the arrow object, r,  of a suggested calendar date if not a holiday."""
        Holiday = django_apps.get_model(*'edc_appointment.holiday'.split('.'))
        holidays = [obj.day for obj in Holiday.objects.all().order_by('day')]
        if r.date() not in holidays:
            return r
        return None

    def available_datetime(self, suggested_datetime, window_delta=None, taken_datetimes=None):
        """Returns a datetime closest to the suggested datetime based on the configuration of the facility.

        To exclude datetimes other than holidays, pass a list of datetimes to `taken_datetimes`."""
        suggested = self.as_arrow_utc(suggested_datetime)
        if not window_delta:
            window_delta = relativedelta(months=1)
        taken = [self.as_arrow_utc(dt) for dt in taken_datetimes or []]
        maximum = self.as_arrow_utc(suggested.datetime + window_delta)
        for r in arrow.Arrow.span_range('day', suggested.datetime, maximum.datetime):
            # add back time to arrow object, r
            r = arrow.Arrow.fromdatetime(datetime.combine(r[0].date(), suggested.time()))
            # see if available
            if r.datetime.weekday() in self.weekdays and (suggested.date() <= r.date() < maximum.date()):
                if (self.not_holiday(r) and r.date() not in [d.date() for d in taken] and
                        self.open_slot_on(r)):
                    return r.datetime
        return suggested.datetime
