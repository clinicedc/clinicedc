from edc_action_item.models import ActionModelMixin
from edc_identifier.model_mixins import (
    NonUniqueSubjectIdentifierFieldMixin,
    TrackingModelMixin,
)
from edc_model.models import BaseUuidModel
from edc_offstudy.constants import END_OF_STUDY_ACTION
from edc_sites.models import SiteModelMixin
from edc_visit_schedule.model_mixins import OffScheduleModelMixin

from ..constants import LOSS_TO_FOLLOWUP_ACTION
from ..model_mixins import LossToFollowupModelMixin


class LossToFollowup(
    NonUniqueSubjectIdentifierFieldMixin,
    LossToFollowupModelMixin,
    SiteModelMixin,
    ActionModelMixin,
    TrackingModelMixin,
    BaseUuidModel,
):
    action_name = LOSS_TO_FOLLOWUP_ACTION

    tracking_identifier_prefix = "LF"

    class Meta(LossToFollowupModelMixin.Meta, BaseUuidModel.Meta):
        pass


class OffSchedule(
    OffScheduleModelMixin, ActionModelMixin, TrackingModelMixin, BaseUuidModel,
):

    action_name = END_OF_STUDY_ACTION

    tracking_identifier_prefix = "ST"

    class Meta(OffScheduleModelMixin.Meta, BaseUuidModel.Meta):
        pass
