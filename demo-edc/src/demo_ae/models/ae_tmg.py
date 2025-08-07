from edc_adverse_event.model_mixins import AeTmgModelMixin
from edc_model.models import BaseUuidModel


class AeTmg(AeTmgModelMixin, BaseUuidModel):
    class Meta(AeTmgModelMixin.Meta, BaseUuidModel.Meta):
        verbose_name = "AE TMG Report"
