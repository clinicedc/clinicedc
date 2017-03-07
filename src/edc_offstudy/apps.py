import sys

from django.apps import AppConfig as DjangoAppConfig
from django.apps import apps as django_apps


class EdcOffstudyAppConfigError(Exception):
    pass

ATTR = 0
MODEL_LABEL = 1


class AppConfig(DjangoAppConfig):
    name = 'edc_offstudy'
    verbose_name = 'Edc Offstudy'

    def ready(self):
        sys.stdout.write('Loading {} ...\n'.format(self.verbose_name))
        # sys.stdout.write('  * using offstudy models from \'{}\'\n'.format(self.app_label))
        sys.stdout.write(' Done loading {}.\n'.format(self.verbose_name))
