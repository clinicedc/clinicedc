from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    name = "edc_pharmacy"
    verbose_name = "Edc Pharmacy"
    has_exportable_data = True
    include_in_administration_section = True
