from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    name = 'edc_lab_dashboard'
    url_namespace = 'edc_lab_dashboard'
