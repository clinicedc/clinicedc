from django.db import models
from edc_model.models import BaseUuidModel
from edc_pylabels.models import LabelConfiguration
from edc_utils import get_utcnow
from sequences import get_next_value

from ...exceptions import AllocationError
from ..prescription import Rx
from ..proxy_models import RegisteredSubjectProxy
from .stock_request_item import StockRequestItem


class Allocation(BaseUuidModel):

    allocation_identifier = models.CharField(max_length=36, unique=True, null=True, blank=True)

    allocation_datetime = models.DateTimeField(default=get_utcnow)

    registered_subject = models.ForeignKey(
        RegisteredSubjectProxy,
        verbose_name="Subject",
        on_delete=models.PROTECT,
        null=True,
        blank=False,
    )

    rando_sid = models.IntegerField(verbose_name="SID", null=True)

    stock_request_item = models.OneToOneField(
        StockRequestItem,
        verbose_name="Stock request item",
        on_delete=models.PROTECT,
        null=True,
        blank=False,
    )

    rx = models.ForeignKey(Rx, on_delete=models.PROTECT, null=True, blank=False)

    label_configuration = models.ForeignKey(
        LabelConfiguration, on_delete=models.PROTECT, null=True, blank=False
    )

    def __str__(self):
        return self.allocation_identifier

    def save(self, *args, **kwargs):
        if not self.allocation_identifier:
            self.allocation_identifier = f"{get_next_value(self._meta.label_lower):06d}"
        if not self.stock_request_item:
            raise AllocationError("Stock request item may not be null")
        super().save(*args, **kwargs)

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Allocation"
        verbose_name_plural = "Allocations"
