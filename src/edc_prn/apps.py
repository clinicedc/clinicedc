from django.apps import AppConfig as DjangoAppConfig

from .site_prn_forms import site_prn_forms


class AppConfig(DjangoAppConfig):
    name = "edc_prn"

    def ready(self):
        site_prn_forms.autodiscover()
