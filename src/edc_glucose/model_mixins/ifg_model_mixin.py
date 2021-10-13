from django.db import models
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from edc_constants.constants import NOT_APPLICABLE
from edc_lab.choices import GLUCOSE_UNITS_NA, RESULT_QUANTIFIER
from edc_lab.constants import EQ

from ..contants import GLUCOSE_HIGH_READING


class IfgModelMixin(models.Model):
    """A model mixin of fields for the IFG"""

    ifg_value = models.DecimalField(
        verbose_name=format_html("IFG level"),
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=f"A `HIGH` reading may be entered as {GLUCOSE_HIGH_READING}",
    )

    ifg_quantifier = models.CharField(
        verbose_name=format_html("IFG quantifier"),
        max_length=10,
        choices=RESULT_QUANTIFIER,
        default=EQ,
    )

    ifg_units = models.CharField(
        verbose_name="IFG units",
        max_length=15,
        choices=GLUCOSE_UNITS_NA,
        default=NOT_APPLICABLE,
    )

    ifg_datetime = models.DateTimeField(
        verbose_name=mark_safe("<u>Time</u> IFG level measured"),
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True
