from django.conf import settings
from django.db import models
from edc_model.models import datetime_not_future
from edc_utils import get_utcnow


class AeSusarFieldsModelMixin(models.Model):

    ae_initial = models.ForeignKey(
        f"{settings.ADVERSE_EVENT_APP_LABEL}.aeinitial", on_delete=models.PROTECT
    )

    report_datetime = models.DateTimeField(
        verbose_name="Report date and time",
        validators=[datetime_not_future],
        default=get_utcnow,
    )

    submitted_datetime = models.DateTimeField(
        verbose_name="AE SUSAR submitted on",
        validators=[datetime_not_future],
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True
