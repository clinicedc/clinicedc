import sys

from django.apps import apps as django_apps
from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    name = 'edc_timepoint'
    verbose_name = 'Edc Timepoint'
    timepoint_models = {
        'example.examplemodel': {
            'datetime_field': 'report_datetime',
            'status_field': 'example_status',
            'closed_status': 'finish'
        }
    }  # list of _meta.labellower

    def ready(self):
        from .signals import update_timepoint_on_post_save
        sys.stdout.write('Loading {} ...\n'.format(self.verbose_name))
        for label in self.timepoint_models:
            sys.stdout.write(' * {} is a timepoint.\n'.format(label))
        sys.stdout.write(' Done loading {}.\n'.format(self.verbose_name))

    @property
    def model(self):
        return django_apps.get_model(self.app_label, 'timepointstatus')
