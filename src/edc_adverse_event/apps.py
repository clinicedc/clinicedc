from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    name = "edc_adverse_event"
    verbose_name = "Edc Adverse Event"
    has_exportable_data = True
    include_in_administration_section = True
