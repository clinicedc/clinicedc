from django.db import models
from edc_model.models import BaseUuidModel, HistoricalRecords
from edc_utils import get_utcnow
from sequences import get_next_value

from .stock import Stock
from .stock_label_batch import StockLabelBatch


class Manager(models.Manager):
    use_in_migrations = True


class StockLabelItem(BaseUuidModel):
    """A model that represents a stock label.

    A stock label is created by request from the stock table"""

    label_identifier = models.CharField(max_length=36, unique=True, null=True, blank=True)

    batch = models.ForeignKey(StockLabelBatch, on_delete=models.PROTECT)

    stock = models.OneToOneField(Stock, on_delete=models.PROTECT)

    label_datetime = models.DateTimeField(default=get_utcnow)

    printed_datetime = models.DateTimeField(null=True, blank=True)

    confirmed_datetime = models.DateTimeField(null=True, blank=True)

    objects = Manager()

    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        if not self.label_identifier:
            self.label_identifier = get_next_value(self._meta.label_lower)
        super().save(*args, **kwargs)

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Stock label item"
        verbose_name_plural = "Stock label item"
