from django.db import models

from ..choices import REPORT_STATUS
from ..validators import datetime_not_future


class ReportStatusModelMixin(models.Model):
    report_status = models.CharField(
        verbose_name="What is the status of this report?",
        max_length=25,
        choices=REPORT_STATUS,
    )

    report_closed_datetime = models.DateTimeField(
        blank=True,
        null=True,
        validators=[datetime_not_future],
        verbose_name="Date and time report closed.",
    )

    class Meta:
        abstract = True
