import arrow
import csv

from django.apps import apps as django_apps
from django.conf import settings
from datetime import datetime


class HolidayImportError(Exception):
    pass


def get_holidays(country=None, path=None, model=None):
    data = {}
    if path:
        with open(path, 'r') as f:
            reader = csv.DictReader(
                f, fieldnames=['local_date', 'label', 'country'])
            for row in reader:
                if row['country'].lower() == country.lower():
                    try:
                        datetime.strptime(
                            row['local_date'], '%Y-%m-%d')
                    except ValueError as e:
                        raise HolidayImportError(
                            f'Invalid format when importing from '
                            f'{path}. Got \'{e}\'')
                    data.update(
                        {row['local_date']: row['label']})
    else:
        model_cls = django_apps.get_model(model)
        for obj in model_cls.objects.all():
            data.update({obj.local_date: obj.label})
    return data


class Holidays:

    def __init__(self, country=None, path=None, model=None):
        self.time_zone = settings.TIME_ZONE
        self.country = country

    def __repr__(self):
        return f'{self.__class__.__name__}()<country={self.country}, time_zone={self.time_zone}>)'

    def __iter__(self):
        return iter(self.holidays.items())

    @property
    def holidays(self):
        app_config = django_apps.get_app_config('edc_facility')
        return app_config.holidays

    def is_holiday(self, utc_datetime=None):
        local_date = self.local_date(utc_datetime=utc_datetime)
        return str(local_date) in self.holidays

    def local_date(self, utc_datetime=None):
        utc = arrow.Arrow.fromdatetime(utc_datetime)
        return utc.to(self.time_zone).date()
