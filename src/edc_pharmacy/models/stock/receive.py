from uuid import uuid4

from django.db import models
from edc_model.models import BaseUuidModel, HistoricalRecords
from edc_utils import get_utcnow

from ..storage import Location
from .order import Order


class Manager(models.Manager):
    use_in_migrations = True


class Receive(BaseUuidModel):

    receive_identifier = models.CharField(max_length=36, unique=True)

    receive_datetime = models.DateTimeField(default=get_utcnow)

    location = models.ForeignKey(Location, on_delete=models.PROTECT)

    order = models.ForeignKey(Order, on_delete=models.PROTECT)

    objects = Manager()

    history = HistoricalRecords()

    def __str__(self):
        return f"{self.order}: recv'd on {self.receive_datetime}"

    def save(self, *args, **kwargs):
        if not self.receive_identifier:
            self.receive_identifier = str(uuid4())
        super().save(*args, **kwargs)

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Stock: Receive"
        verbose_name_plural = "Stock: Receive"
