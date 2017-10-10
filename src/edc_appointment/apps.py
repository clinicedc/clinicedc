from dateutil.relativedelta import MO, TU, WE, TH, FR
import os
import sys

from django.apps import AppConfig as DjangoAppConfig
from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from .facility import Facility


class AppConfig(DjangoAppConfig):
    name = 'edc_appointment'
    verbose_name = "Edc Appointments"
    app_label = 'edc_appointment'
    default_appt_type = 'clinic'
    country = 'botswana'
    file_holidays = False
    holiday_csv_path = os.path.join(settings.BASE_DIR, 'holidays.csv')
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

    def get_facility(self, name):
        try:
            facility = self.facilities[name]
        except KeyError:
            raise ImproperlyConfigured(
                'Error creating appointment. Facility {} does not exist.'.format(name))
        return facility

    def visit_model_reverse_attr(self, key=None):
        return self.visit_reverse_relations.get(key, 'subjectvisit')
