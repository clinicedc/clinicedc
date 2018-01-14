from edc_base.model_mixins import BaseUuidModel

from .managers import CrfMetadataManager, RequisitionMetadataManager
from .model_mixins.metadata_models import CrfModelMixin, RequisitionMetadataModelMixin


class CrfMetadata(CrfModelMixin, BaseUuidModel):

    objects = CrfMetadataManager()

    class Meta(CrfModelMixin.Meta):
        app_label = 'edc_metadata'


class RequisitionMetadata(RequisitionMetadataModelMixin, BaseUuidModel):

    objects = RequisitionMetadataManager()

    class Meta(RequisitionMetadataModelMixin.Meta):
        app_label = 'edc_metadata'
