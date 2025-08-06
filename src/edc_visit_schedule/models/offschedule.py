from edc_model.models import BaseUuidModel
from edc_sites.model_mixins import SiteModelMixin

from ..model_mixins import OffScheduleModelMixin


class OffSchedule(SiteModelMixin, OffScheduleModelMixin, BaseUuidModel):
    """A model used by the system. Records a subject as no longer on
    a schedule.
    """

    class Meta(OffScheduleModelMixin.Meta, BaseUuidModel.Meta):
        pass
