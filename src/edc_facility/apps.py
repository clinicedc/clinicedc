import os
import sys

from dateutil.relativedelta import MO, TU, WE, TH, FR
from django.apps import AppConfig as DjangoAppConfig
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.management.color import color_style

from .facility import Facility
# from .holidays import get_holidays

style = color_style()


class AppConfig(DjangoAppConfig):
    _holidays = {}
    name = 'edc_facility'
    verbose_name = "Edc Facility"
    holiday_path = settings.HOLIDAY_FILE
    holiday_model = 'edc_facility.holiday'

    facilities = {
        'clinic': Facility(
            name='clinic',
            days=[MO, TU, WE, TH, FR],
            slots=[100, 100, 100, 100, 100],
            country='botswana')}

    def ready(self):

        sys.stdout.write(f'Loading {self.verbose_name} ...\n')
        for facility in self.facilities.values():
            sys.stdout.write(f' * {facility}.\n')
            if self.holiday_path:
                if not os.path.exists(self.holiday_path):
                    sys.stdout.write(style.ERROR(
                        f'File not found! settings.HOLIDAY_FILE=\'{self.holiday_path}\'. \n'))
                else:
                    sys.stdout.write(
                        f' * reading holidays from {self.holiday_path}.\n')
        sys.stdout.write(f' Done loading {self.verbose_name}.\n')

    def get_facility(self, name=None):
        try:
            facility = self.facilities[name]
        except KeyError:
            raise ImproperlyConfigured(
                f'Error creating appointment. Facility {name} does not exist.')
        return facility
