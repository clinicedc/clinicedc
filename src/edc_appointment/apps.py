import sys

from dateutil.relativedelta import MO, TU, WE, TH, FR
from django.apps import AppConfig as DjangoAppConfig
from django.apps import apps as django_apps
from django.conf import settings
from edc_facility import Facility


class AppConfig(DjangoAppConfig):

    _holidays = {}
    name = 'edc_appointment'
    verbose_name = "Edc Appointments"
    appointment_model = 'edc_appointment.appointment'
    default_appt_type = 'clinic'
    visit_reverse_relations = {
        None: 'subjectvisit',
        'edc_appointment.appointment': 'subjectvisit',
    }

    def ready(self):
        from .signals import (
            create_appointments_on_post_save,
            appointment_post_save,
            delete_appointments_on_post_delete)

        sys.stdout.write(f'Loading {self.verbose_name} ...\n')
        sys.stdout.write(f' * using {self.appointment_model}.\n')
        sys.stdout.write(f' Done loading {self.verbose_name}.\n')

    def visit_model_reverse_attr(self, key=None):
        return self.visit_reverse_relations.get(key, 'subjectvisit')


if settings.APP_NAME == 'edc_appointment':

    from edc_facility.apps import AppConfig as BaseEdcFacilityAppConfig

    class EdcFacilityAppConfig(BaseEdcFacilityAppConfig):
        country = 'botswana'
        facilities = {
            'clinic': Facility(
                name='clinic',
                days=[MO, TU, WE, TH, FR],
                slots=[100, 100, 100, 100, 100])}
