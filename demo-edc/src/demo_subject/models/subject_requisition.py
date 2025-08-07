from edc_lab.managers import RequisitionManager as Manager  # noqa
from edc_lab.model_mixins import RequisitionModelMixin
from edc_model.models import BaseUuidModel


class SubjectRequisition(RequisitionModelMixin, BaseUuidModel):
    class Meta(RequisitionModelMixin.Meta, BaseUuidModel.Meta):
        verbose_name = "Subject Requisition"
        verbose_name_plural = "Subject Requisitions"
