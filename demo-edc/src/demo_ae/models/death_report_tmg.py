from edc_adverse_event.model_mixins import DeathReportTmgModelMixin
from edc_model.models import BaseUuidModel


class DeathReportTmg(DeathReportTmgModelMixin, BaseUuidModel):
    class Meta(DeathReportTmgModelMixin.Meta, BaseUuidModel.Meta):
        pass
