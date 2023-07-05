from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist


class EdcSitesCountryError(Exception):
    pass


def get_current_country(request=None):
    """Returns the country, defaults to that of the default site."""
    country = None
    if site := getattr(request, "site", None):
        country = site.siteprofile.country
    else:
        site_model_cls = django_apps.get_model("sites.site")
        try:
            country = site_model_cls.objects.get_current().siteprofile.country
        except ObjectDoesNotExist:
            pass
    return country
