import sys

from django.conf import settings
from edc_action_item.models import ActionModelMixin
from edc_consent.model_mixins import RequiresConsentFieldsModelMixin
from edc_identifier.model_mixins import TrackingModelMixin
from edc_model.models import BaseUuidModel
from edc_sites.models import CurrentSiteManager, SiteModelMixin

from .action_items import SUBJECT_LOCATOR_ACTION
from .model_mixins import LocatorModelMixin, LocatorManager

if settings.APP_NAME == "edc_locator" and "makemigrations" not in sys.argv:
    from .tests import models  # noqa


class SubjectLocator(
    LocatorModelMixin,
    RequiresConsentFieldsModelMixin,
    ActionModelMixin,
    TrackingModelMixin,
    SiteModelMixin,
    BaseUuidModel,
):
    """A model completed by the user to that captures participant
    locator information and permission to contact.
    """

    action_name = SUBJECT_LOCATOR_ACTION

    tracking_identifier_prefix = "SL"

    on_site = CurrentSiteManager()

    objects = LocatorManager()

    def natural_key(self):
        return (self.subject_identifier,)

    natural_key.dependencies = ["sites.Site"]

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Subject Locator"
