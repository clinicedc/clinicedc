import sys

from dateutil.relativedelta import MO, TU, WE, TH, FR

from django.apps import AppConfig as DjangoAppConfig
from django.apps import apps as django_apps

from .facility import Facility
from django.core.exceptions import ImproperlyConfigured


class AppConfig(DjangoAppConfig):
    name = 'edc_appointment'
    verbose_name = "Edc Appointments"
    app_label = 'edc_example'
    default_appt_type = 'clinic'
    facilities = {
        'clinic': Facility(name='clinic', days=[MO, TU, WE, TH, FR], slots=[100, 100, 100, 100, 100])}

    def ready(self):
        from .signals import create_appointments_on_post_save, appointment_post_save
        sys.stdout.write('Loading {} ...\n'.format(self.verbose_name))
        sys.stdout.write(' * using {}.{}.\n'.format(self.app_label, self.model_name))
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
            raise ImproperlyConfigured('Error creating appointment. Facility {} does not exist.'.format(name))
        return facility
