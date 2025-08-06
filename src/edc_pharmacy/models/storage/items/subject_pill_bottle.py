from django.db import models

from .pill_bottle import PillBottle
from .pill_bottle_model_mixin import PillBottleModelMixin


class SubjectPillBottle(PillBottleModelMixin):
    rando_sid = models.CharField(max_length=25)

    subject_identifier = models.CharField(max_length=50, null=True)

    source_container = models.ForeignKey(
        PillBottle, on_delete=models.PROTECT, blank=True, null=True
    )

    class Meta(PillBottleModelMixin.Meta):
        verbose_name = "Subject Pill Bottle"
        verbose_name_plural = "Subject Pill Bottles"
