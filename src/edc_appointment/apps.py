from django.apps import AppConfig
from django.apps import apps as django_apps


class EdcAppointmentAppConfig(AppConfig):
    name = 'edc_appointment'
    verbose_name = "Appointments"
    model = None
    appointments_days_forward = 0
    appointments_per_day_max = 30
    use_same_weekday = True
    allowed_iso_weekdays = '1234567'
    default_appt_type = 'clinic'

    @property
    def appointment_model(self):
        return django_apps.get_model(*self.model)
