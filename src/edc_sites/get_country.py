from __future__ import annotations

from typing import TYPE_CHECKING

from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist

if TYPE_CHECKING:
    from django.contrib.sites.models import Site
    from django.core.handlers.wsgi import WSGIRequest


class EdcSitesCountryError(Exception):
    pass


def get_current_country(request: WSGIRequest | None = None, site: Site | None = None):
    """Returns the country, defaults to that of the default site."""
    country = None
    site = site or getattr(request, "site", None)
    if site:
        country = site.siteprofile.country
    else:
        site_model_cls = django_apps.get_model("sites.site")
        try:
            country = site_model_cls.objects.get_current().siteprofile.country
        except ObjectDoesNotExist:
            pass
    return country
