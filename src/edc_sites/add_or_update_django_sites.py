import sys

from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

from .single_site import SiteDomainRequiredError


class InvalidSiteError(Exception):
    pass


class ReviewerSiteSaveError(Exception):
    pass


def add_or_update_django_sites(apps=None, sites=None, verbose=None):
    """Removes default site and adds/updates given `sites`, etc.

    Title is stored in SiteProfile.

    kwargs:
        * sites: format
            sites = (
                (<site_id>, <site_name>, <title>),
                ...)
    """
    if verbose:
        sys.stdout.write(f"  * updating sites.\n")
    apps = apps or django_apps
    site_model_cls = apps.get_model("sites", "Site")
    site_model_cls.objects.filter(name="example.com").delete()
    for single_site in sites:
        if verbose:
            sys.stdout.write(f"  * {single_site.name}.\n")
        site_obj = get_or_create_site_obj(single_site, apps)
        get_or_create_site_profile_obj(single_site, site_obj, apps)


def get_or_create_site_obj(single_site, apps):
    if "multisite" in settings.INSTALLED_APPS and not single_site.domain:
        raise SiteDomainRequiredError(
            f"Domain required when using `multisite`. Got None for `{single_site.name}`"
        )
    site_model_cls = apps.get_model("sites", "Site")
    try:
        site_obj = site_model_cls.objects.get(pk=single_site.site_id)
    except ObjectDoesNotExist:
        site_obj = site_model_cls.objects.create(
            pk=single_site.site_id, name=single_site.name, domain=single_site.domain
        )
    else:
        site_obj.name = single_site.name
        site_obj.domain = single_site.domain
        site_obj.save()
    return site_obj


def get_or_create_site_profile_obj(single_site, site_obj, apps):
    site_profile_model_cls = apps.get_model("edc_sites", "SiteProfile")
    opts = dict(
        title=single_site.title,
        country=single_site.country,
        country_code=single_site.country_code,
        description=single_site.description or single_site.title,
    )
    try:
        site_profile = site_profile_model_cls.objects.get(site=site_obj)
    except ObjectDoesNotExist:
        site_profile_model_cls.objects.create(site=site_obj, **opts)
    else:
        for k, v in opts.items():
            setattr(site_profile, k, v)
        site_profile.save()
