from django.db import models

from edc_base.model.models import BaseModel


class BaseSequence(BaseModel):

    device_id = models.IntegerField(default=99)

    objects = models.Manager()

    def __str__(self):
        return self.pk

    class Meta:
        abstract = True
