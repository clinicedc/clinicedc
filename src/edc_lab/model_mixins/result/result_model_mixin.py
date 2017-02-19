from django.db import models
from django.utils import timezone

from ..panel_model_mixin import PanelModelMixin


class ResultModelMixin(PanelModelMixin, models.Model):

    report_datetime = models.DateTimeField(
        null=True)

    pending_datetime = models.DateTimeField(
        default=timezone.now)

    pending = models.BooleanField(default=True)

    resulted_datetime = models.DateTimeField(
        default=timezone.now)

    resulted = models.BooleanField(default=False)

    class Meta:
        abstract = True
