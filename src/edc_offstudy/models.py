from edc_action_item.models import ActionNoManagersModelMixin
from edc_identifier.managers import SubjectIdentifierManager
from edc_model.models import BaseUuidModel, HistoricalRecords
from edc_sites.managers import CurrentSiteManager
from edc_sites.model_mixins import SiteModelMixin

from .constants import END_OF_STUDY_ACTION
from .model_mixins import OffstudyModelMixin


class SubjectOffstudy(
    OffstudyModelMixin,
    SiteModelMixin,
    ActionNoManagersModelMixin,
    BaseUuidModel,
):
    action_name = END_OF_STUDY_ACTION

    objects = SubjectIdentifierManager()

    on_site = CurrentSiteManager()

    history = HistoricalRecords()

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Subject Offstudy"
        verbose_name_plural = "Subject Offstudy"
        indexes = (*ActionNoManagersModelMixin.Meta.indexes, *BaseUuidModel.Meta.indexes)
