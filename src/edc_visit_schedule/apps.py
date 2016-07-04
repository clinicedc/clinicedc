from django.apps import AppConfig
from django_crypto_fields.apps import DjangoCryptoFieldsAppConfig


class EdcVisitScheduleAppConfig(AppConfig):
    name = 'edc_visit_schedule'
    verbose_name = "Visit Schedule"
    model = None
