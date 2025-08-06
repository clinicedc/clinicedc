from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    name = "edc_consent"
    verbose_name = "Edc Consent"
    include_in_administration_section = True
