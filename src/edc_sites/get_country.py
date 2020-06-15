from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist


class EdcSitesCountryError(Exception):
    pass


def get_current_country():
    """Returns the country, defaults to that of the default site."""
    site_model_cls = django_apps.get_model("sites.site")
    try:
        return site_model_cls.objects.get_current().siteprofile.country
    except ObjectDoesNotExist:
        return None
