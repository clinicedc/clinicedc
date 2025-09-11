from __future__ import annotations

import sys

from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist

from ..single_site import SingleSite
from .get_or_create_site_obj import get_or_create_site_obj
from .get_or_create_site_profile_obj import get_or_create_site_profile_obj


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
    try:
        obj = site_model_cls.objects.get(id=1)
    except ObjectDoesNotExist:
        pass
    else:
        # Delete will fail if you have an unmanaged model with an FK
        # to Site and `on_delete` is something other than DO_NOTHING.
        # See the comment in edc_appconfig.apps about why we might
        # unregister `create_default_site` post_migrate signal.
        obj.delete()
    if not single_sites:
        single_sites = get_sites().all().values()
    if not single_sites:
        raise UpdateDjangoSitesError("No sites have been registered.")
    for single_site in single_sites:
        if single_site.name == "edc_sites.sites":
            continue
        if verbose:
            sys.stdout.write(f"  * SingleSite: {single_site.site_id}: {single_site.domain}.\n")
        site_obj = get_or_create_site_obj(single_site, apps)
        if verbose:
            sys.stdout.write(f"    - Site model: {site_obj.id}: {site_obj.domain}.\n")
        get_or_create_site_profile_obj(single_site, site_obj, apps)
    return single_sites
