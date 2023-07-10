from edc_action_item.models import ActionNoManagersModelMixin
from edc_consent.model_mixins import RequiresConsentFieldsModelMixin
from edc_identifier.managers import SubjectIdentifierManager
from edc_model import models as edc_models
from edc_sites.models import CurrentSiteManager, SiteModelMixin

from .constants import END_OF_STUDY_ACTION
from .model_mixins import OffstudyModelMixin


class SubjectOffstudy(
    RequiresConsentFieldsModelMixin,
    OffstudyModelMixin,
    SiteModelMixin,
    ActionNoManagersModelMixin,
    edc_models.BaseUuidModel,
):
    action_name = END_OF_STUDY_ACTION

    objects = SubjectIdentifierManager()

    on_site = CurrentSiteManager()

    history = edc_models.HistoricalRecords()

    class Meta(edc_models.BaseUuidModel.Meta):
        verbose_name = "Subject Offstudy"
        verbose_name_plural = "Subject Offstudy"
