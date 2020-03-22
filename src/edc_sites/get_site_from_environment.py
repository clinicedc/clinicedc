import os
import sys
from django.core.management import color_style
from importlib import import_module

from .get_site_id import get_site_id
from .get_sites_by_country import get_sites_by_country

style = color_style()


class EdcSiteFromEnvironmentError(Exception):
    pass


def get_site_from_environment(
    default_site_name=None, default_country=None, app_name=None, sites_module_name=None,
):
    """Returns the country, site_id and site_name for settings
    extracted from the environment.

    * Assumes the sites module has `sites`, e.g. inte_sites.sites
    * Assumes the values can be extracted from DJANGO_SETTINGS_MODULE.
    * The expected format of the value of DJANGO_SETTINGS_MODULE is
      `<appname>.settings.<country>.<sitename>`.

    This is for use in mutlisite deployments where each site has identical settings
    values other than COUNTRY and SITE_ID.
    """

    sites_module = import_module(f"{sites_module_name}.sites")
    if os.environ.get("DJANGO_SETTINGS_MODULE") in [
        f"{app_name}.settings.defaults",
        f"{app_name}.settings",
    ]:

        sys.stderr.write(
            style.ERROR(
                "Using defaults for country and site. Assuming a test environment (get_site_from_environment) "
                f"Got DJANGO_SETTINGS_MODULE=`{os.environ.get('DJANGO_SETTINGS_MODULE')}`.\n"
            )
        )

        country = default_country
        site_name = default_site_name
        site_id = get_site_id(
            site_name,
            sites=get_sites_by_country(
                country=country, all_sites=sites_module.all_sites
            ),
        )
    else:
        _app_name, _, country, site_name = os.environ.get(
            "DJANGO_SETTINGS_MODULE"
        ).split(".")
        if app_name != _app_name:
            raise EdcSiteFromEnvironmentError(
                "Invalid app_name extracted from DJANGO_SETTINGS_MODULE."
            )
        site_id = get_site_id(
            site_name,
            sites=get_sites_by_country(
                country=country, all_sites=sites_module.all_sites
            ),
        )
    return country, site_id, site_name
