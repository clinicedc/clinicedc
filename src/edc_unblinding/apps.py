from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    name = "edc_unblinding"
    verbose_name = "Edc Unblinding"
    has_exportable_data = True
    include_in_administration_section = True
