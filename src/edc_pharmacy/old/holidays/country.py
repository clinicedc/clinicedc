import arrow
from dateutil.relativedelta import relativedelta
from django.apps import apps as django_apps
from django.conf import settings

from .holidays import Holidays


class Country:
    """Returns holidays for given country.
    """

    holidays_cls = Holidays

    def __init__(
        self,
        country=None,
        time_zone=None,
        skip_holiday=None,
        skip_weekend=None,
        **kwargs
    ):
        app_config = django_apps.get_app_config("edc_pharma")
        self.skip_holiday = skip_holiday
        self.skip_weekend = skip_weekend
        self.name = country or app_config.country
        self.time_zone = time_zone or settings.TIME_ZONE
        self.holidays = self.holidays_cls(country=self.name, **kwargs)

    def local_date(self, utc_datetime=None):
        utc = arrow.Arrow.fromdatetime(utc_datetime)
        return utc.to(self.time_zone).date()

    def is_workday(self, utc_datetime=None):
        return not self.is_weekend(utc_datetime) and not self.is_holiday(utc_datetime)

    def is_holiday(self, utc_datetime=None):
        local_date = self.local_date(utc_datetime)
        return self.holidays.is_holiday(local_date=local_date)

    def is_weekend(self, utc_datetime=None):
        return utc_datetime.weekday() in [6, 7]

    def move_to_workday(self, utc_datetime=None):
        check_again = False
        if self.skip_holiday:
            while self.is_holiday(utc_datetime=utc_datetime):
                utc_datetime = utc_datetime + relativedelta(days=1)
                check_again = True
        if self.skip_weekend:
            while self.is_weekend(utc_datetime=utc_datetime):
                utc_datetime = utc_datetime + relativedelta(days=1)
                check_again = True
        if check_again:
            self.move_to_workday(utc_datetime=utc_datetime)
        return utc_datetime

    def __str__(self):
        return self.name
