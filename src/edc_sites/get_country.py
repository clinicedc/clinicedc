from django.apps import apps as django_apps
from django.conf import settings


class EdcSitesCountryError(Exception):
    pass


def get_country():
    edc_site_model_cls = django_apps.get_model("edc_sites.edcsite")
    return edc_site_model_cls.objects.get(id=settings.SITE_ID).country
