from uuid import uuid4

from django.db import models
from edc_model.models import BaseUuidModel
from edc_utils import get_utcnow

from .location import Location


class Room(BaseUuidModel):
    room_identifier = models.CharField(max_length=36, default=uuid4, unique=True)

    room_datetime = models.DateTimeField(default=get_utcnow)

    name = models.CharField(max_length=25, unique=True)

    description = models.TextField(null=True)

    location = models.ForeignKey(Location, on_delete=models.PROTECT)

    def __str__(self):
        return f"Room {self.name}"

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Room"
        verbose_name_plural = "Rooms"
