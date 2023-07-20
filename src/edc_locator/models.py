from edc_action_item.models import ActionModelMixin
from edc_consent.model_mixins import RequiresConsentFieldsModelMixin
from edc_model.models import BaseUuidModel
from edc_sites.models import CurrentSiteManager, SiteModelMixin

from .action_items import SUBJECT_LOCATOR_ACTION
from .model_mixins import LocatorManager, LocatorModelMixin


class SubjectLocator(
    LocatorModelMixin,
    RequiresConsentFieldsModelMixin,
    ActionModelMixin,
    SiteModelMixin,
    BaseUuidModel,
):
    """A model completed by the user that captures participant
    locator information and permission to contact.
    """

    action_name = SUBJECT_LOCATOR_ACTION

    objects = LocatorManager()

    on_site = CurrentSiteManager()

    def natural_key(self):
        return (self.subject_identifier,)

    natural_key.dependencies = ["sites.Site"]

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Subject Locator"
        verbose_name_plural = "Subject Locators"
