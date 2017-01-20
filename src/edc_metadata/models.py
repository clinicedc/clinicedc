from edc_base.model.models import BaseUuidModel

from .model_mixins.metadata_models import CrfModelMixin, RequisitionModelMixin


class CrfMetadata(CrfModelMixin, BaseUuidModel):

    class Meta(CrfModelMixin.Meta):
        app_label = 'edc_metadata'


class RequisitionMetadata(RequisitionModelMixin, BaseUuidModel):

    class Meta(RequisitionModelMixin.Meta):
        app_label = 'edc_metadata'
