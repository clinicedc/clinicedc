from django.apps import AppConfig
from django_crypto_fields.apps import DjangoCryptoFieldsAppConfig


class EdcAppointmentAppConfig(AppConfig):
    name = 'edc_appointment'
    verbose_name = "Appointments"


class TestEdcAppointmentApp(EdcAppointmentAppConfig):
    name = 'edc_appointment'
    model = ('example', 'appointment')


class DjangoCryptoFieldsApp(DjangoCryptoFieldsAppConfig):
    name = 'django_crypto_fields'
    model = ('example', 'crypt')
    crypt_model_using = 'default'
