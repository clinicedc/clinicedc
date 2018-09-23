import sys

from datetime import datetime
from dateutil.tz import gettz
from django.apps import AppConfig as DjangoAppConfig
from django.apps import apps as django_apps
from django.conf import settings


class AppConfig(DjangoAppConfig):
    name = 'edc_registration'
    verbose_name = 'Edc Registration'
    app_label = 'edc_registration'
    has_exportable_data = True

    def ready(self):
        from .signals import update_registered_subject_from_model_on_post_save
        sys.stdout.write(f'Loading {self.verbose_name} ...\n')
        sys.stdout.write(f'  * using {self.app_label}.registeredsubject\n')
        sys.stdout.write(f' Done loading {self.verbose_name}.\n')

    @property
    def model(self):
        return django_apps.get_model(self.app_label, 'registeredsubject')


if 'edc_registration' in settings.APP_NAME:

    from edc_protocol.apps import AppConfig as BaseEdcProtocolAppConfig

    class EdcProtocolAppConfig(BaseEdcProtocolAppConfig):
        protocol = 'BHP092'
        protocol_name = 'Ambition'
        protocol_number = '092'
        protocol_title = ''
        site_code = '40'
        site_name = 'Gaborone'
        study_open_datetime = datetime(
            2016, 12, 31, 0, 0, 0, tzinfo=gettz('UTC'))
        study_close_datetime = datetime(
            2019, 12, 31, 23, 59, 59, tzinfo=gettz('UTC'))
