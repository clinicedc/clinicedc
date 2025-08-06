from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    name = "edc_offstudy"
    verbose_name = "Edc Offstudy"
    has_exportable_data = True
    include_in_administration_section = False
