from django.db import models
from django.db.models import PROTECT
from edc_model import models as edc_models

from edc_lab.utils import get_requisition_model_name


class CrfWithRequisitionModelMixin(models.Model):

    requisition = models.ForeignKey(
        get_requisition_model_name(),
        on_delete=PROTECT,
        related_name="+",
        verbose_name="Requisition",
        null=True,
        blank=True,
        help_text="Start typing the requisition identifier or select one from this visit",
    )

    assay_datetime = models.DateTimeField(
        verbose_name="Result Report Date and Time",
        validators=[edc_models.datetime_not_future],
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True
