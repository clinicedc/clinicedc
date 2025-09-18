from uuid import uuid4

from django.db import models
from django.utils import timezone

from edc_model.models import BaseUuidModel

from .room import Room


class Shelf(BaseUuidModel):
    shelf_identifier = models.CharField(max_length=36, default=uuid4, unique=True)

    shelf_datetime = models.DateTimeField(default=timezone.now)

    name = models.CharField(max_length=25, unique=True)

    description = models.TextField(default="")

    room = models.ForeignKey(Room, on_delete=models.PROTECT)

    def __str__(self):
        return f"Shelf {self.name}"

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Shelf"
        verbose_name_plural = "Shelves"
