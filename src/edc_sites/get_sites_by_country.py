from django.conf import settings
from django_extensions.management.color import color_style
from importlib import import_module

from .get_country import get_country

style = color_style()


def get_sites_by_country(country=None, all_sites=None, sites_module_name=None):
    """Returns a sites tuple for the country."""
    if not all_sites:
        sites_module = import_module(
            sites_module_name or settings.EDC_SITES_MODULE_NAME
        )
        all_sites = sites_module.all_sites
    return all_sites.get(country or get_country())
