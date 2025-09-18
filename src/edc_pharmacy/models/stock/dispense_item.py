import django.utils.timezone
from django.db import models
from sequences import get_next_value

from edc_model.models import BaseUuidModel, HistoricalRecords
from edc_sites.model_mixins import SiteModelMixin
from edc_visit_schedule.model_mixins import VisitCodeFieldsModelMixin

from .dispense import Dispense
from .stock import Stock


class Manager(models.Manager):
    use_in_migrations = True


class DispenseItem(SiteModelMixin, VisitCodeFieldsModelMixin, BaseUuidModel):
    """A model for the stock dispensing transaction."""

    dispense_item_identifier = models.CharField(
        max_length=36,
        unique=True,
        null=True,
        blank=True,
        help_text="A sequential unique identifier set by the EDC",
    )

    dispense_item_datetime = models.DateTimeField(default=django.utils.timezone.now)

    dispense = models.ForeignKey(
        Dispense,
        verbose_name="Dispense",
        on_delete=models.PROTECT,
        null=True,
        blank=False,
    )

    stock = models.OneToOneField(Stock, on_delete=models.PROTECT)

    objects = Manager()

    history = HistoricalRecords()

    def __str__(self):
        return self.dispense_item_identifier

    def save(self, *args, **kwargs):
        self.site = self.dispense.site
        if not self.dispense_item_identifier:
            self.dispense_item_identifier = f"{get_next_value(self._meta.label_lower):010d}"
        super().save(*args, **kwargs)

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Dispense item"
        verbose_name_plural = "Dispense items"
