import pytz

from django.apps import apps as django_apps
from datetime import datetime
from collections import OrderedDict
from calendar import Calendar
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, MONTHLY
from django.utils import timezone
from test.test_itertools import take


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

    def holidays(self, year, month, time):
        """Returns a list of datetimes that are holidays, includes time to help with comparision."""
        Holiday = django_apps.get_model('edc_appointment', 'holiday')
        return Holiday.objects.for_month(year, month, time=time)

    def slots_per_day(self, day):
        try:
            slots_per_day = self.config.get(str(day))
        except KeyError:
            slots_per_day = 0
        return slots_per_day

    @property
    def weekdays(self):
        return [d.weekday for d in self.days]

    def open_slot_on(self, suggested_datetime):
        return True

    def available_datetime(self, suggested_datetime, window_days=None, taken_datetimes=None):
        """Returns a datetime closest to the suggested datetime based on the configuration of the facility.

        To exclude datetimes other than holidays, pass a list of datetimes to `taken_datetimes`."""
        taken_datetimes = taken_datetimes or []
        if not timezone.is_aware(suggested_datetime):
            raise TypeError('naive datetime for suggested_datetime. Got {}'.format(suggested_datetime.isoformat()))
        available_datetime = None
        window_days = window_days or 30
        max_datetime = suggested_datetime + relativedelta(days=window_days)
        calendar = Calendar()
        year = suggested_datetime.year
        for month in [dt.month for dt in rrule(MONTHLY, dtstart=suggested_datetime, until=max_datetime)]:
            month_datetimes = []
            for dt in calendar.itermonthdates(year, month):
                if dt.month == month and dt >= suggested_datetime.date() and dt < max_datetime.date():
                    month_datetimes.append(
                        timezone.make_aware(
                            datetime.combine(dt, suggested_datetime.time()), timezone=pytz.timezone('UTC')))
            for dt in month_datetimes:
                if dt not in self.holidays(year, month, time=suggested_datetime.time()) and dt not in taken_datetimes:
                    if dt.weekday() in self.weekdays:
                        if self.open_slot_on(dt):
                            available_datetime = dt
                            break
                        else:
                            available_datetime = None
            if available_datetime:
                break
        return available_datetime or suggested_datetime
