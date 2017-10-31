from collections import OrderedDict
from dateutil.relativedelta import relativedelta

from .schedule_validator import ScheduleValidator


class ScheduleCollection(OrderedDict):
    """A class that represents a "period" of schedule.

    Is contained by a "schedule". A period is measured in days,
    weeks, and years.
    """
    validator = ScheduleValidator

    def add(self, schedule=None):
        self.update({schedule.name: schedule})
        self.validator(schedules=self)

    @property
    def next_timepoint(self):
        last_schedule = self.last()
        if self.last():
            return last_schedule.period.end_datetime + relativedelta(days=1)

    def last(self):
        try:
            key = next(reversed(self))
        except Exception:
            pass
        else:
            return self[key]

    def first(self):
        try:
            key = next(self)
        except Exception as e:
            print(e)
        else:
            return self[key]
