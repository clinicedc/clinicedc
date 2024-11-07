from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from edc_model.models import BaseUuidModel
from edc_utils import get_utcnow
from sequences import get_next_value

from ...choices import STOCK_UPDATE


class StockUpdate(BaseUuidModel):

    update_identifier = models.CharField(max_length=36, unique=True, null=True, blank=True)

    report_datetime = models.DateTimeField(default=get_utcnow)

    source_model = models.CharField(verbose_name="Task", max_length=100, choices=STOCK_UPDATE)

    item_count = models.IntegerField(
        default=0, validators=[MinValueValidator(1), MaxValueValidator(20)]
    )

    identifiers = models.TextField(
        verbose_name="Scan labels here",
        help_text="One per line, no more than 20 per document",
    )

    def save(self, *args, **kwargs):
        if not self.update_identifier:
            self.order_item_identifier = f"{get_next_value(self._meta.label_lower):06d}"
        super().save(*args, **kwargs)

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Stock update"
        verbose_name_plural = "Stock updates"
