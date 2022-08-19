from django.db import models
from edc_lab.constants import EQ
from edc_reportable import PERCENT

from ..constants import GLUCOSE_HIGH_READING


class Hba1cModelMixin(models.Model):
    """A model mixin of fields for the HbA1c"""

    hba1c_value = models.DecimalField(
        verbose_name="HbA1c Reading",
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=f"A `HIGH` reading may be entered as {GLUCOSE_HIGH_READING}",
    )

    hba1c_quantifier = models.CharField(
        verbose_name="HbA1c quantifier",
        max_length=10,
        default=EQ,
        editable=False,
    )

    hba1c_units = models.CharField(
        verbose_name="HbA1c units", max_length=15, default=PERCENT, editable=False
    )

    hba1c_datetime = models.DateTimeField(
        verbose_name="Date/time HbA1c measured",
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True
