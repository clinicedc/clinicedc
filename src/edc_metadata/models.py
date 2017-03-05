from edc_base.model_mixins import BaseUuidModel

from .model_mixins.metadata_models import CrfModelMixin, RequisitionModelMixin
from .managers import CrfMetadataManager, RequisitionMetadataManager


class CrfMetadata(CrfModelMixin, BaseUuidModel):

    objects = CrfMetadataManager()

    def natural_key(self):
        return (
            self.model, self.subject_identifier,
            self.schedule_name, self.visit_schedule_name, self.visit_code, )

    class Meta(CrfModelMixin.Meta):
        app_label = 'edc_metadata'


class RequisitionMetadata(RequisitionModelMixin, BaseUuidModel):

    objects = RequisitionMetadataManager()

    def natural_key(self):
        return (
            self.panel_name, self.model, self.subject_identifier,
            self.schedule_name, self.visit_schedule_name, self.visit_code, )

    class Meta(RequisitionModelMixin.Meta):
        app_label = 'edc_metadata'
