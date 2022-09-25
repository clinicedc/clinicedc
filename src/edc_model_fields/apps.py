from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    name = "edc_model_fields"
    verbose_name = "EDC Model Fields"
