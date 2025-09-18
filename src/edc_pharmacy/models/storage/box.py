from uuid import uuid4

from django.db import models
from django.utils import timezone

from edc_model.models import BaseUuidModel

from .shelf import Shelf


class Box(BaseUuidModel):
    box_identifier = models.CharField(max_length=36, default=uuid4, unique=True)

    box_datetime = models.DateTimeField(default=timezone.now)

    name = models.CharField(max_length=25, unique=True)

    description = models.TextField(default="")

    shelf = models.ForeignKey(Shelf, on_delete=models.PROTECT, null=True)

    def __str__(self):
        return f"Box {self.name}"

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Box"
        verbose_name_plural = "Boxes"
