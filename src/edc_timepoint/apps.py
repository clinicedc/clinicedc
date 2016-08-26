import sys

from django.apps import apps as django_apps
from django.apps import AppConfig as DjangoAppConfig

from edc_timepoint.timepoint import Timepoint


class AppConfig(DjangoAppConfig):
    name = 'edc_timepoint'
    verbose_name = 'Edc Timepoint'
    timepoints = [
        Timepoint(
            model='example.examplemodel',
            datetime_field='report_datetime',
            status_field='example_status',
            closed_status='finish')
    ]

    def ready(self):
        from .signals import update_timepoint_on_post_save
        sys.stdout.write('Loading {} ...\n'.format(self.verbose_name))
        temp = {}
        for timepoint in self.timepoints:
            sys.stdout.write(' * {} is a timepoint.\n'.format(timepoint))
            temp[str(timepoint)] = timepoint
        self.timepoints = temp
        sys.stdout.write(' Done loading {}.\n'.format(self.verbose_name))

    @property
    def model(self):
        return django_apps.get_model(self.app_label, 'timepointstatus')
