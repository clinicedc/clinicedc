import sys

from django.conf import settings
from edc_action_item.model_mixins import ActionItemModelMixin
from edc_base.model_mixins import BaseUuidModel
from edc_base.sites.site_model_mixin import SiteModelMixin
from edc_base.model_managers import HistoricalRecords
from edc_consent.model_mixins import RequiresConsentFieldsModelMixin
from edc_identifier.model_mixins import TrackingIdentifierModelMixin

from .model_mixins import LocatorModelMixin, LocatorManager
from .action_items import SubjectLocatorAction
from django.contrib.sites.managers import CurrentSiteManager

if settings.APP_NAME == 'edc_locator' and 'makemigrations' not in sys.argv:
    from .tests import models


class SubjectLocator(LocatorModelMixin, RequiresConsentFieldsModelMixin,
                     ActionItemModelMixin, SiteModelMixin, TrackingIdentifierModelMixin,
                     BaseUuidModel):
    """A model completed by the user to that captures participant
    locator information and permission to contact.
    """
    action_cls = SubjectLocatorAction

    tracking_identifier_prefix = 'SL'

    on_site = CurrentSiteManager()

    objects = LocatorManager()

    history = HistoricalRecords()

    def natural_key(self):
        return (self.subject_identifier, )
    natural_key.dependencies = ['sites.Site']

    class Meta:
        verbose_name = 'Subject Locator'
