from django.conf import settings
from edc_action_item.model_mixins import ActionItemModelMixin
from edc_base.model_mixins import BaseUuidModel
from edc_base.model_managers import HistoricalRecords
from edc_consent.model_mixins import RequiresConsentNonCrfModelMixin

from .model_mixins import LocatorModelMixin
from .action_items import SubjectLocatorAction

if settings.APP_NAME == 'edc_locator':
    from .tests import models


class SubjectLocator(LocatorModelMixin, RequiresConsentNonCrfModelMixin,
                     ActionItemModelMixin, BaseUuidModel):
    """A model completed by the user to that captures participant
    locator information and permission to contact.
    """
    action_cls = SubjectLocatorAction

    history = HistoricalRecords()

    class Meta(RequiresConsentNonCrfModelMixin.Meta):
        consent_model = 'ambition_subject.subjectconsent'
