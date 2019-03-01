import sys

from django.apps import apps as django_apps
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist


class ReviewerSiteSaveError(Exception):
    pass


def add_or_update_django_sites(apps=None, sites=None, fqdn=None, verbose=None):
    """Removes default site and adds/updates given `sites`, etc.

    kwargs:
        * sites: format
            sites = (
                (<site_id>, <site_name>, <description>),
                ...)
    """

    fqdn = fqdn or "example.com"
    apps = apps or django_apps
    Site = apps.get_model("sites", "Site")
    Site.objects.filter(name="example.com").delete()
    for site_id, site_name, _ in sites:
        try:
            site_obj = Site.objects.get(pk=site_id)
        except ObjectDoesNotExist:
            Site.objects.create(
                pk=site_id, name=site_name, domain=f"{site_name}.{fqdn}"
            )
        else:
            site_obj.name = site_name
            site_obj.domain = f"{site_name}.{fqdn}"
            site_obj.save()
    if verbose:
        sys.stdout.write(f"Updated sites for {fqdn}.\n")
        sys.stdout.flush()


def raise_on_save_if_reviewer(site_id=None):
    site_id = Site.objects.get_current().id if site_id is None else site_id
    try:
        REVIEWER_SITE_ID = settings.REVIEWER_SITE_ID
    except AttributeError:
        REVIEWER_SITE_ID = 0
    if int(site_id) == int(REVIEWER_SITE_ID) and "migrate" not in sys.argv:
        raise ReviewerSiteSaveError(
            f"Adding or changing data has been disabled. "
            f"Got site '{site_id}' is a 'review only' site code."
        )
