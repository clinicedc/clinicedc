from edc_action_item.models import ActionModelMixin
from edc_model.models import BaseUuidModel
from edc_offstudy.constants import END_OF_STUDY_ACTION
from edc_sites.model_mixins import SiteModelMixin
from edc_visit_schedule.model_mixins import OffScheduleModelMixin


class OffSchedule(
    OffScheduleModelMixin,
    SiteModelMixin,
    ActionModelMixin,
    BaseUuidModel,
):
    action_name = END_OF_STUDY_ACTION

    class Meta(OffScheduleModelMixin.Meta, BaseUuidModel.Meta):
        pass
