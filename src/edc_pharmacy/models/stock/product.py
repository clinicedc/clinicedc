from django.db import models
from django.db.models import PROTECT
from sequences import get_next_value

from edc_model.models import BaseUuidModel, HistoricalRecords

from ..medication import Assignment, Formulation


class Manager(models.Manager):
    use_in_migrations = True


class Product(BaseUuidModel):

    product_identifier = models.CharField(
        max_length=36,
        unique=True,
        null=True,
        blank=True,
        help_text="A sequential unique identifier set by the EDC",
    )

    name = models.CharField(max_length=50, blank=True, help_text="Leave blank to use default")

    formulation = models.ForeignKey(Formulation, on_delete=PROTECT)

    assignment = models.ForeignKey(Assignment, on_delete=PROTECT, null=True, blank=False)

    objects = Manager()

    history = HistoricalRecords()

    def __str__(self):
        """Note: For unblinded users, add assignment in ModelAdmin where a request
        object is available.
        """
        return self.formulation.get_description_with_assignment(self.assignment)

    def save(self, *args, **kwargs):
        if not self.product_identifier:
            self.product_identifier = f"{get_next_value(self._meta.label_lower):06d}"
        if not self.name:
            self.name = self.formulation.get_product_description()
        super().save(*args, **kwargs)

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Product"
        verbose_name_plural = "Product"
