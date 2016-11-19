from django.apps import apps as django_apps
from datetime import datetime
from collections import OrderedDict
from calendar import Calendar
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, MONTHLY
from django.utils import timezone


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

    def holidays(self, year, month):
        Holiday = django_apps.get_model('edc_appointment', 'holiday')
        return Holiday.objects.for_month(year, month)

    def slots_per_day(self, day):
        try:
            slots_per_day = self.config.get(str(day))
        except KeyError:
            slots_per_day = 0
        return slots_per_day

    @property
    def weekdays(self):
        return [d.weekday for d in self.days]

    def open_slot_on(self, suggested_date):
        return True

    def available_datetime(self, suggested_datetime, window_days=None):
        if not timezone.is_aware(suggested_datetime):
            raise TypeError('naive datetime for suggested_datetime. Got {}'.format(suggested_datetime.isoformat()))
        available_datetime = None
        window_days = window_days or 30
        max_datetime = suggested_datetime + relativedelta(days=window_days)
        calendar = Calendar()
        year = suggested_datetime.year
        for month in [dt.month for dt in rrule(MONTHLY, dtstart=suggested_datetime, until=max_datetime)]:
            dates = []
            for dt in calendar.itermonthdates(year, month):
                if dt.month == month and dt >= suggested_datetime.date() and dt < max_datetime.date():
                    dates.append(dt)
            for dt in dates:
                if dt not in self.holidays(year, month):
                    if dt.weekday() in self.weekdays:
                        if self.open_slot_on(dt):
                            available_datetime = timezone.make_aware(datetime.combine(dt, suggested_datetime.time()))
                            break
                        else:
                            available_datetime = None
            if available_datetime:
                break
        return available_datetime or suggested_datetime
