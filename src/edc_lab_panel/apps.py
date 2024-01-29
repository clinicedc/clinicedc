from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    name = "edc_lab_panel"
    verbose_name = "Edc Lab Panel"
    include_in_administration_section = False
