from django.db import models
from django.utils.html import format_html
from edc_constants.constants import NOT_APPLICABLE
from edc_lab.choices import GLUCOSE_UNITS_NA, RESULT_QUANTIFIER
from edc_lab.constants import EQ


class OgttModelMixin(models.Model):
    """A model mixin of fields for the OGTT"""

    ogtt_base_datetime = models.DateTimeField(
        verbose_name=format_html("<u>Time</u> oral glucose solution was given"),
        null=True,
        blank=True,
        help_text="(glucose solution given)",
    )

    ogtt_value = models.DecimalField(
        verbose_name=format_html(
            "Blood glucose <u>level</u> 2-hours " "after oral glucose solution given"
        ),
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="A `HIGH` reading may be entered as 9999.99",
    )

    ogtt_quantifier = models.CharField(
        max_length=10,
        choices=RESULT_QUANTIFIER,
        default=EQ,
    )

    ogtt_units = models.CharField(
        verbose_name="Units (Blood glucose 2hrs after...)",
        max_length=15,
        default=NOT_APPLICABLE,
        choices=GLUCOSE_UNITS_NA,
        blank=False,
    )

    ogtt_datetime = models.DateTimeField(
        verbose_name=format_html(
            "<u>Time</u> blood glucose measured 2-hours " "after oral glucose solution given"
        ),
        blank=True,
        null=True,
        help_text="(2 hours after glucose solution given)",
    )

    class Meta:
        abstract = True
