import sys

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
            closed_status='finish'),
        Timepoint(
            model='edc_appointment.appointment',
            datetime_field='report_datetime',
            status_field='appt_status',
            closed_status='complete')
    ]

    def ready(self):
        from .signals import update_timepoint_on_post_save
        sys.stdout.write('Loading {} ...\n'.format(self.verbose_name))
        timepoints = {}
        for timepoint in self.timepoints:
            sys.stdout.write(' * {} is a timepoint.\n'.format(timepoint))
            timepoints[str(timepoint)] = timepoint
        self.timepoints = timepoints  # converted to dict.
        sys.stdout.write(' Done loading {}.\n'.format(self.verbose_name))
