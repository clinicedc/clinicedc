from django.db import models
from edc_constants.constants import CLOSED, OPEN
from edc_model.models import BaseUuidModel, HistoricalRecords
from edc_utils import get_utcnow
from sequences import get_next_value


class Manager(models.Manager):
    use_in_migrations = True


class StockLabelBatch(BaseUuidModel):

    batch_identifier = models.CharField(max_length=36, unique=True, null=True, blank=True)

    batch_datetime = models.DateTimeField(default=get_utcnow)

    item_count = models.IntegerField(verbose_name="Item count", null=True)

    labels = models.TextField(verbose_name="Labels", null=True, blank=True)

    status = models.CharField(
        max_length=25,
        choices=((OPEN, OPEN.title()), (CLOSED, CLOSED.title())),
        default=OPEN,
    )

    objects = Manager()

    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        if not self.batch_identifier:
            self.batch_identifier = get_next_value(self._meta.label_lower)
        super().save(*args, **kwargs)

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Stock label batch"
        verbose_name_plural = "Stock label batches"
