from edc_action_item.models import ActionModelMixin
from edc_model.models import BaseUuidModel
from edc_offstudy.constants import END_OF_STUDY_ACTION
from edc_visit_schedule.model_mixins import OffScheduleModelMixin


class OffSchedule(
    OffScheduleModelMixin,
    ActionModelMixin,
    BaseUuidModel,
):

    action_name = END_OF_STUDY_ACTION

    tracking_identifier_prefix = "ST"

    class Meta(OffScheduleModelMixin.Meta, BaseUuidModel.Meta):
        pass
