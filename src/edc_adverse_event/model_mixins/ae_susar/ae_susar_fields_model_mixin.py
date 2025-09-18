from django.db import models
from django.utils import timezone

from edc_model.validators import datetime_not_future

from ...utils import get_adverse_event_app_label


class AeSusarFieldsModelMixin(models.Model):
    ae_initial = models.ForeignKey(
        f"{get_adverse_event_app_label()}.aeinitial", on_delete=models.PROTECT
    )

    report_datetime = models.DateTimeField(
        verbose_name="Report date and time",
        validators=[datetime_not_future],
        default=timezone.now,
    )

    submitted_datetime = models.DateTimeField(
        verbose_name="AE SUSAR submitted on",
        validators=[datetime_not_future],
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True
