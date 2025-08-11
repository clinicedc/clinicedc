from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    name = "tests"
    verbose_name = "tests"
    app_label = "tests"
