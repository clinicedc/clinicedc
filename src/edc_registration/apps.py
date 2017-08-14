import sys

from datetime import datetime
from dateutil.tz import gettz

from django.apps import apps as django_apps
from django.conf import settings

from django.apps import AppConfig as DjangoAppConfig


from edc_protocol.apps import AppConfig as BaseEdcProtocolAppConfig, SubjectType, Cap


class AppConfig(DjangoAppConfig):
    name = 'edc_registration'
    verbose_name = 'Edc Registration'
    app_label = 'edc_registration'

    def ready(self):
        from .signals import update_registered_subject_from_model_on_post_save
        sys.stdout.write('Loading {} ...\n'.format(self.verbose_name))
        sys.stdout.write(
            '  * using {}.registeredsubject\n'.format(self.app_label, ))
        sys.stdout.write(' Done loading {}.\n'.format(self.verbose_name))

    @property
    def model(self):
        return django_apps.get_model(self.app_label, 'registeredsubject')

if 'edc_registration' in settings.APP_NAME:
    class EdcProtocolAppConfig(BaseEdcProtocolAppConfig):
        protocol = 'BHP091'
        protocol_number = '091'
        protocol_name = 'Edc Registration'
        protocol_title = ''
        subject_types = [
            SubjectType('subject', 'Research Subject',
                        Cap(model_name='edc_registration.subjectconsent', max_subjects=9999)),
        ]
        study_open_datetime = datetime(
            2016, 12, 31, 0, 0, 0, tzinfo=gettz('UTC'))
        study_close_datetime = datetime(
            2019, 12, 31, 0, 0, 0, tzinfo=gettz('UTC'))

        @property
        def site_name(self):
            return 'Test_Community'

        @property
        def site_code(self):
            return '01'
