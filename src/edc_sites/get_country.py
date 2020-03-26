from django.apps import apps as django_apps

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist


class EdcSitesCountryError(Exception):
    pass


def get_country(site_id=None):
    """Returns the country if site profile is set up, otherwise None."""
    model_cls = django_apps.get_model("edc_sites.siteprofile")
    try:
        return model_cls.objects.get(site__id=site_id or settings.SITE_ID).country
    except ObjectDoesNotExist:
        return None
