import arrow
import csv
import os

from datetime import datetime
from django.apps import apps as django_apps
from django.conf import settings


class HolidayImportError(Exception):
    pass


def get_holidays(country=None, path=None, model=None):
    data = {}
    if path:
        try:
            if not os.path.exists(path):
                raise HolidayFileNotFoundError(path)
        except TypeError:
            raise HolidayError(f'Invalid path. Got {path}.')
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


class HolidayFileNotFoundError(Exception):
    pass


class HolidayError(Exception):
    pass


class Holidays:

    model = 'edc_facility.holiday'

    def __init__(self, country=None, path=None, model=None):
        self._holidays = {}
        self.country = country
        if not self.country:
            self.country = settings.COUNTRY
        self.path = path
        if not self.path:
            self.path = settings.HOLIDAY_FILE
        self.model = model or self.model
        self.time_zone = settings.TIME_ZONE

    def __repr__(self):
        return f'{self.__class__.__name__}()<country={self.country}, time_zone={self.time_zone}>)'

    def __iter__(self):
        return iter(self.holidays.items())

    @property
    def holidays(self):
        """Returns a dictionary of holidays for this country as
        {local_date: label, ...}.
        """
        if not self._holidays:
            self._holidays = get_holidays(
                country=self.country, path=self.path, model=self.model)
        return self._holidays

#     @property
#     def holidays(self):
#         app_config = django_apps.get_app_config('edc_facility')
#         return app_config.holidays

    def is_holiday(self, utc_datetime=None):
        local_date = self.local_date(utc_datetime=utc_datetime)
        return str(local_date) in self.holidays

    def local_date(self, utc_datetime=None):
        utc = arrow.Arrow.fromdatetime(utc_datetime)
        return utc.to(self.time_zone).date()
