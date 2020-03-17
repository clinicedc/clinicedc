from django.apps import AppConfig as DjangoAppConfig
from django.conf import settings


class AppConfig(DjangoAppConfig):
    name = "edc_model_admin"
