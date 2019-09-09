import sys

from django.apps import apps as django_apps
from django.conf import settings


class ReviewerSiteSaveError(Exception):
    pass


def raise_on_save_if_reviewer(site_id=None):
    Site = django_apps.get_model("sites", "Site")
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
