import sys

from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist


class InvalidSiteError(Exception):
    pass


class ReviewerSiteSaveError(Exception):
    pass


SITE_ID = 0
SITE_NAME = 1
SITE_TITLE = 2
SITE_DESCRIPTION = 3


def add_or_update_django_sites(apps=None, sites=None, fqdn=None, verbose=None):
    """Removes default site and adds/updates given `sites`, etc.

    Title is stored in SiteProfile.

    kwargs:
        * sites: format
            sites = (
                (<site_id>, <site_name>, <title>),
                ...)
    """
    if verbose:
        sys.stdout.write(f"  * updating sites for {fqdn}.\n")
    fqdn = fqdn or "example.com"
    apps = apps or django_apps
    Site = apps.get_model("sites", "Site")
    Site.objects.filter(name="example.com").delete()
    for site in sites:
        if verbose:
            sys.stdout.write(f"  * {site[SITE_NAME]}.\n")
        site_obj = get_or_create_site_obj(site, fqdn, apps)
        get_or_create_site_profile_obj(site, site_obj, apps)


def get_or_create_site_obj(site, fqdn, apps):
    Site = apps.get_model("sites", "Site")
    try:
        site_obj = Site.objects.get(pk=site[SITE_ID])
    except ObjectDoesNotExist:
        site_obj = Site.objects.create(
            pk=site[SITE_ID], name=site[SITE_NAME],
            domain=f"{site[SITE_NAME]}.{fqdn}"
        )
    else:
        site_obj.name = site[SITE_NAME]
        site_obj.domain = f"{site[SITE_NAME]}.{fqdn}"
        site_obj.save()
    return site_obj


def get_or_create_site_profile_obj(site, site_obj, apps):
    SiteProfile = apps.get_model("edc_sites", "SiteProfile")
    try:
        site_profile = SiteProfile.objects.get(site=site_obj)
    except ObjectDoesNotExist:
        opts = dict(
            title=site[SITE_TITLE],
            site=site_obj)
        try:
            opts.update(description=site[SITE_DESCRIPTION])
        except IndexError:
            opts.update(description=None)
        SiteProfile.objects.create(**opts)
    else:
        site_profile.title = site[SITE_TITLE]
        try:
            site_profile.description = site[SITE_DESCRIPTION]
        except IndexError:
            site_profile.description = None
        site_profile.save()
