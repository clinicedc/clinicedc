from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    name = "edc_transfer"
    verbose_name = "Edc Transfer"
