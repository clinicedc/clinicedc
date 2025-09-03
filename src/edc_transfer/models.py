from edc_list_data.model_mixins import ListModelMixin
from edc_model.models import BaseUuidModel
from edc_sites.managers import CurrentSiteManager

from .model_mixins import SubjectTransferModelMixin


class TransferReasons(ListModelMixin):
    class Meta(ListModelMixin.Meta):
        verbose_name = "Transfer Reasons"
        verbose_name_plural = "Transfer Reasons"


class SubjectTransfer(SubjectTransferModelMixin, BaseUuidModel):

    on_site = CurrentSiteManager()

    class Meta(SubjectTransferModelMixin.Meta, BaseUuidModel.Meta):
        verbose_name = "Subject transfer"
        verbose_name_plural = "Subject transfers"
