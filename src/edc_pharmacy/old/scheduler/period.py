from edc_utils import get_utcnow

import arrow
from dateutil.relativedelta import relativedelta
from django.apps import apps as django_apps


class Period:

    """A class that represents a "period" of schedule.

    Is contained by a "schedule". A period is measured in days,
    weeks, and years. Given a timepoint_datetime the class calculates
    start_date and end_date excluding weekends and holidays.
    """

    app_config = django_apps.get_app_config("edc_pharma")

    def __init__(self, start_datetime=None, unit=None, duration=None, **kwargs):
        self.start_datetime = start_datetime or get_utcnow()
        rdelta = relativedelta(**{unit: duration or 0})
        end_datetime = self.start_datetime + rdelta
        self.end_datetime = end_datetime - relativedelta(days=1)
        facility = self.app_config.facility
        self.workdays = []
        if self.start_datetime and self.end_datetime:
            for arr in arrow.Arrow.span_range(
                "day", self.start_datetime, self.end_datetime
            ):
                available_datetime = facility.available_datetime(
                    suggested_datetime=arr[0].datetime, window_delta=rdelta
                )
                if available_datetime:
                    self.workdays.append(available_datetime)

    def __repr__(self):
        return f"{self.start_date.date()}, {self.end_date.date()}"
