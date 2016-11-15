import sys

from django.apps import AppConfig as DjangoAppConfig
from django.apps import apps as django_apps


class AppConfig(DjangoAppConfig):
    name = 'edc_appointment'
    verbose_name = "Edc Appointments"
    app_label = 'edc_example'
    appointments_days_forward = 0
    appointments_per_day_max = 30
    use_same_weekday = True
    weekday = 2
    allowed_iso_weekdays = '12345'
    default_appt_type = 'clinic'

    def ready(self):
        from .signals import create_appointments_on_post_save, appointment_post_save
        sys.stdout.write('Loading {} ...\n'.format(self.verbose_name))
        sys.stdout.write(' * using {}.{}.\n'.format(self.app_label, self.model_name))
        sys.stdout.write(' Done loading {}.\n'.format(self.verbose_name))

    @property
    def model(self):
        return django_apps.get_model(self.app_label, self.model_name)

    @property
    def model_name(self):
        return 'appointment'
