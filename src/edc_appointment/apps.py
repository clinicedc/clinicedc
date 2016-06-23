from django.apps import AppConfig
from django_crypto_fields.apps import DjangoCryptoFieldsAppConfig


class EdcAppointmentAppConfig(AppConfig):
    name = 'edc_appointment'
    verbose_name = "Appointments"
    model = None


class DjangoCryptoFieldsApp(DjangoCryptoFieldsAppConfig):
    name = 'django_crypto_fields'
    model = ('django_crypto_fields', 'crypt')
    crypt_model_using = 'default'
