from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    name = "edc_locator"
    verbose_name = "Edc Locator"
    has_exportable_data = True
    include_in_administration_section = True
