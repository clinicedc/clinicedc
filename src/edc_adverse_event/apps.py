from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    name = "edc_adverse_event"
    verbose_name = "Edc Adverse Event"
    include_in_administration_section = True
