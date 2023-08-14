from django.db import models
from edc_model.validators import datetime_not_future
from edc_utils import get_utcnow

from ...utils import get_adverse_event_app_label


class AesiFieldsModelMixin(models.Model):
    ae_initial = models.ForeignKey(
        f"{get_adverse_event_app_label()}.aeinitial", on_delete=models.PROTECT
    )

    report_datetime = models.DateTimeField(
        verbose_name="Report date and time",
        validators=[datetime_not_future],
        default=get_utcnow,
    )

    submitted_datetime = models.DateTimeField(
        verbose_name="AE of Special Interest submitted on",
        validators=[datetime_not_future],
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True
