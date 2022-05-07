from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    name = "edc_lab_results"
    verbose_name = "Edc Blood Results"
