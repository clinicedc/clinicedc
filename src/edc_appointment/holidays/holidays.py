import csv
import arrow

from django.apps import apps as django_apps
from django.conf import settings


class Holidays:

    def __init__(self, country=None, path=None, timezone=None):
        app_config = django_apps.get_app_config('edc_appointment')
        path = app_config.holiday_csv_path
        self.holidays = {}
        self.time_zone = timezone or settings.TIME_ZONE
        self.country = country or app_config.country
        self.path = path or self.path
        with open(self.path, 'r') as f:
            reader = csv.DictReader(
                f, fieldnames=['local_date', 'label', 'country'])
            for row in reader:
                if row['country'] == self.country:
                    self.holidays.update({row['local_date']: row['label']})

    def __repr__(self):
        return f'{self.__class__.__name__}(country={self.country}, path={self.path})'

    def is_holiday(self, utc_datetime=None):
        local_date = self.local_date(utc_datetime=utc_datetime)
        return str(local_date) in self.holidays
      
    def local_date(self, utc_datetime=None):
        utc = arrow.Arrow.fromdatetime(utc_datetime)
        return utc.to(self.time_zone).date()
