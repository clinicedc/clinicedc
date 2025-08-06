from uuid import uuid4

from django.db import models
from edc_utils import get_utcnow

from ..box import Box
from ..container_type import ContainerType


class ContainerModelMixin(models.Model):
    container_identifier = models.CharField(max_length=36, default=uuid4, unique=True)

    container_datetime = models.DateTimeField(default=get_utcnow)

    name = models.CharField(max_length=25, unique=True)

    container_type = models.ForeignKey(ContainerType, on_delete=models.PROTECT)

    box = models.ForeignKey(Box, on_delete=models.PROTECT, null=True)

    description = models.TextField(null=True)

    contains_uniquely_identifiable_items = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.container_type.name} {self.name}"

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = self.container_identifier
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
        verbose_name = "Item"
        verbose_name_plural = "Items"
