from edc_model.models import BaseUuidModel
from edc_sites.model_mixins import SiteModelMixin

from ..model_mixins import OnScheduleModelMixin


class OnSchedule(SiteModelMixin, OnScheduleModelMixin, BaseUuidModel):
    """A model used by the system. Auto-completed by subject_consent."""

    class Meta(OnScheduleModelMixin.Meta, BaseUuidModel.Meta):
        pass
