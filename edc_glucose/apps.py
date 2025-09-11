from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    name = "edc_glucose"
    verbose_name = "Edc Glucose"
