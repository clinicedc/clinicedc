from django.db import models
from django.db.models.deletion import PROTECT
from edc_model.models import BaseUuidModel
from edc_utils import get_utcnow

from .data_request import DataRequest


class DataRequestHistory(BaseUuidModel):

    data_request = models.ForeignKey(DataRequest, on_delete=PROTECT)

    archive_filename = models.CharField(max_length=200, null=True)

    emailed_to = models.EmailField(null=True)

    emailed_datetime = models.DateTimeField(null=True)

    summary = models.TextField(null=True)

    exported_datetime = models.DateTimeField(default=get_utcnow)

    class Meta:
        ordering = ("-exported_datetime",)
        verbose_name = "Data Request History"
        verbose_name_plural = "Data Request History"
