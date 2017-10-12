import sys

from dateutil.relativedelta import MO, TU, WE, TH, FR
from django.apps import AppConfig as DjangoAppConfig
from django.apps import apps as django_apps
from edc_facility.facility import Facility
from django.conf import settings


class AppConfig(DjangoAppConfig):
    _holidays = {}
    name = 'edc_appointment'
    verbose_name = "Edc Appointments"
    app_label = 'edc_appointment'
    default_appt_type = 'clinic'
    facilities = {
        'clinic': Facility(
            name='clinic',
            days=[MO, TU, WE, TH, FR],
            slots=[100, 100, 100, 100, 100])}

    visit_reverse_relations = {
        None: 'subjectvisit',
        'edc_appointment.appointment': 'subjectvisit',
    }

    def ready(self):
        from .signals import (
            create_appointments_on_post_save,
            appointment_post_save,
            delete_appointments_on_post_delete)

        sys.stdout.write('Loading {} ...\n'.format(self.verbose_name))
        sys.stdout.write(
            ' * using {}.{}.\n'.format(self.app_label, self.model_name))
        for facility in self.facilities.values():
            sys.stdout.write(' * {}.\n'.format(facility))
        sys.stdout.write(' Done loading {}.\n'.format(self.verbose_name))

    @property
    def model(self):
        return django_apps.get_model(self.app_label, self.model_name)

    @property
    def model_name(self):
        return 'appointment'

    def visit_model_reverse_attr(self, key=None):
        return self.visit_reverse_relations.get(key, 'subjectvisit')


if settings.APP_NAME == 'edc_appointment':

    from edc_facility.apps import AppConfig as BaseEdcFacilityAppConfig

    class EdcFacilityAppConfig(BaseEdcFacilityAppConfig):
        country = 'botswana'
