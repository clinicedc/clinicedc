from __future__ import annotations

import sys

from django.apps import apps as django_apps

from ..single_site import SingleSite
from .get_or_create_site_obj import get_or_create_site_obj
from .get_or_create_site_profile_obj import get_or_create_site_profile_obj


class InvalidSiteError(Exception):
    pass


class UpdateDjangoSitesError(Exception):
    pass


def get_sites():
    from ..site import sites  # prevent circular import

    return sites


def add_or_update_django_sites(
    apps: django_apps | None = None,
    single_sites: list[SingleSite] | tuple[SingleSite] = None,
    verbose: bool | None = None,
):
    """Removes default site and adds/updates given `sites`, etc.

    Title is stored in SiteProfile.

    kwargs:
        * sites: format
            sites = (
                (<site_id>, <site_name>, <title>),
                ...)
    """
    if verbose:
        sys.stdout.write("  * updating sites.\n")
    apps = apps or django_apps
    site_model_cls = apps.get_model("sites", "Site")
    site_model_cls.objects.filter(name="example.com").delete()
    if not single_sites:
        single_sites = get_sites().all().values()
    if not single_sites:
        raise UpdateDjangoSitesError("No sites have been registered.")
    for single_site in single_sites:
        if single_site.name == "edc_sites.sites":
            continue
        if verbose:
            sys.stdout.write(f"  * {single_site.name}.\n")
        site_obj = get_or_create_site_obj(single_site, apps)
        get_or_create_site_profile_obj(single_site, site_obj, apps)
    return single_sites
