from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    name = "edc_registration"
    verbose_name = "Edc Registration"
    app_label = "edc_registration"
    has_exportable_data = True
    include_in_administration_section = True
