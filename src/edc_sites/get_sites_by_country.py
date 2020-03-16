import sys
from importlib import import_module

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django_extensions.management.color import color_style

style = color_style()


def get_sites_by_country(country=None, all_sites=None, sites_module_name=None):
    if not all_sites:
        sites_module = import_module(
            sites_module_name or settings.EDC_SITES_MODULE_NAME
        )
        all_sites = sites_module.all_sites
    if not country:
        try:
            country = settings.COUNTRY
        except ImproperlyConfigured:
            sys.stdout.write(style.ERROR("Defaulting country to Uganda."))
            country = "uganda"
    try:
        country_sites = all_sites[country]
    except KeyError:
        msg = (
            f"Invalid site name. "
            f"Expected one of {list(all_sites.keys())}. "
            f"Got `{country}`."
        )
        raise KeyError(msg)
    return country_sites
