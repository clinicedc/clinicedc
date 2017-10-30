import sys

from dateutil.relativedelta import MO, TU, WE, TH, FR
from django.apps import AppConfig as DjangoAppConfig
from django.conf import settings
from edc_facility import Facility

from .appointment_config import AppointmentConfig


class AppConfig(DjangoAppConfig):

    _holidays = {}
    name = 'edc_appointment'
    verbose_name = "Edc Appointments"
    configurations = [
        AppointmentConfig(
            model='edc_appointment.appointment',
            related_visit_model='edc_appointment.subjectvisit')
    ]

    def ready(self):
        from .signals import (
            create_appointments_on_post_save,
            appointment_post_save,
            delete_appointments_on_post_delete)

        sys.stdout.write(f'Loading {self.verbose_name} ...\n')
        for config in self.configurations:
            sys.stdout.write(f' * {config.name}.\n')
        sys.stdout.write(f' Done loading {self.verbose_name}.\n')

    def get_configuration(self, name=None):
        return [c for c in self.configurations if c.name == name][0]
