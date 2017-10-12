from dateutil.relativedelta import MO, TU, WE, TH, FR

import os
import sys

from django.apps import AppConfig as DjangoAppConfig
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from .facility import Facility
from .holidays import get_holidays


class AppConfig(DjangoAppConfig):
    _holidays = {}
    name = 'edc_facility'
    verbose_name = "Edc Facility"

    country = None
    holiday_path = os.path.join(settings.BASE_DIR, 'holidays.csv')
    holiday_model = 'edc_facility.holiday'

    facilities = {
        'clinic': Facility(
            name='clinic',
            days=[MO, TU, WE, TH, FR],
            slots=[100, 100, 100, 100, 100])}

    def ready(self):

        sys.stdout.write(f'Loading {self.verbose_name} ...\n')
        for facility in self.facilities.values():
            sys.stdout.write(f' * {facility}.\n')
        sys.stdout.write(f' Done loading {self.verbose_name}.\n')

    @property
    def holidays(self):
        """Returns a dictionary of holidays for this country as
        {local_date: label, ...}.
        """
        if not self._holidays:
            self._holidays = get_holidays(
                country=self.country, path=self.holiday_path, model=self.holiday_model)
        return self._holidays

    def get_facility(self, name=None):
        try:
            facility = self.facilities[name]
        except KeyError:
            raise ImproperlyConfigured(
                f'Error creating appointment. Facility {name} does not exist.')
        return facility
