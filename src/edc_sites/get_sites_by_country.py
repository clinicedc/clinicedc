from django_extensions.management.color import color_style

from .get_all_sites import get_all_sites
from .get_country import get_current_country
from .get_sites_module import get_sites_module

style = color_style()


def get_sites_by_country(country=None, all_sites=None, sites_module_name=None):
    """Returns a sites tuple for the country."""
    if not all_sites or get_all_sites():
        all_sites = get_sites_module().all_sites
    return all_sites.get(country or get_current_country())
