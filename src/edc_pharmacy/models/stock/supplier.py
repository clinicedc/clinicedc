from django.db import models
from django.utils import timezone
from sequences import get_next_value

from edc_model.models import BaseUuidModel, HistoricalRecords

from ..model_mixins import AddressModelMixin, ContactModelMixin


class Manager(models.Manager):
    use_in_migrations = True


class Supplier(AddressModelMixin, ContactModelMixin, BaseUuidModel):
    supplier_identifier = models.CharField(max_length=36, unique=True, null=True, blank=True)

    name = models.CharField(max_length=255, unique=True)

    contact = models.CharField(max_length=255, default="", blank=True)

    supplier_datetime = models.DateTimeField(default=timezone.now)

    objects = Manager()

    history = HistoricalRecords()

    def __str__(self):
        return self.name[:35]

    def save(self, *args, **kwargs):
        if not self.supplier_identifier:
            next_id = get_next_value(self._meta.label_lower)
            self.supplier_identifier = f"{next_id:06d}"
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Supplier"
        verbose_name_plural = "Suppliers"
