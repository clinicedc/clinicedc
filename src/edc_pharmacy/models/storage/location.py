from uuid import uuid4

from django.db import models
from edc_model.models import BaseUuidModel
from edc_utils import get_utcnow


class Location(BaseUuidModel):
    location_identifier = models.CharField(max_length=36, default=uuid4, unique=True)

    location_datetime = models.DateTimeField(default=get_utcnow)

    name = models.CharField(max_length=25, unique=True)

    description = models.TextField(null=True)

    def __str__(self):
        return f"Location {self.name} "

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Location"
        verbose_name_plural = "Locations"
