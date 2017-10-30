import os
import sys

from dateutil.relativedelta import MO, TU, WE, TH, FR
from django.apps import AppConfig as DjangoAppConfig
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.management.color import color_style

from .facility import Facility

style = color_style()


class AppConfig(DjangoAppConfig):
    _holidays = {}
    name = 'edc_facility'
    verbose_name = "Edc Facility"
    definitions = {
        'clinic': dict(days=[MO, TU, WE, TH, FR],
                       slots=[100, 100, 100, 100, 100])}

    def ready(self):
        sys.stdout.write(f'Loading {self.verbose_name} ...\n')
        try:
            holiday_path = settings.HOLIDAY_FILE
        except AttributeError:
            holiday_path = None
        else:
            if not os.path.exists(holiday_path):
                sys.stdout.write(style.ERROR(
                    f'File not found! settings.HOLIDAY_FILE=\'{holiday_path}\'. \n'))
            else:
                sys.stdout.write(
                    f' * reading holidays from {holiday_path}.\n')
        for facility in self.facilities.values():
            sys.stdout.write(f' * {facility}.\n')
        sys.stdout.write(f' Done loading {self.verbose_name}.\n')

    @property
    def facilities(self):
        """Returns a dictionary of facilities.
        """
        return {k: Facility(name=k, **v)
                for k, v in self.definitions.items()}

    def get_facility(self, name=None):
        """Returns a facility instance for this name
        if it exists.
        """
        try:
            options = self.definitions[name]
        except KeyError:
            raise ImproperlyConfigured(
                f'Facility {name} does not exist. See {self.name} app_config.definitions')
        return Facility(name=name, **options)
